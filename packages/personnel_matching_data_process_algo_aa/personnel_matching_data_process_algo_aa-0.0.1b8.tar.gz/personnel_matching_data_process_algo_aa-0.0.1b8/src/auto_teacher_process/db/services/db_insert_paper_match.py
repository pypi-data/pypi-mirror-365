from auto_teacher_process.db.db_base import BaseDBProcessor


class PaperInsertDBProcessor(BaseDBProcessor):
    """网页数据插入处理器"""

    def __init__(self, system="db_processor", stage="unkonw_task_name", logger=None):
        super().__init__(system=system, stage=stage, logger=logger)

    def get_all_school_info_and_intl(self):
        query = """
            SELECT school_name, school_name_en FROM product_intl_school_info
            UNION
            SELECT school_name, school_name_en FROM product_school_info
            """
        return self.get_db(query)

    def get_school_name_dict(self):
        school_df_and_intl = self.get_all_school_info_and_intl()
        school_names = school_df_and_intl["school_name"]
        school_names_en = school_df_and_intl["school_name_en"]
        return dict(zip(school_names, school_names_en, strict=False)), dict(zip(school_names_en, school_names, strict=False))

    def get_paper_teacher_data_from_db(self, id_start, id_end):
        query = f"""
                SELECT t.teacher_id, t.derived_teacher_name, t.college_name, t.description, des.omit_description, proj.project_experience, area.research_area, em.email, t.school_name
                FROM derived_teacher_data t
                LEFT JOIN derived_omit_description des ON t.teacher_id = des.teacher_id
                LEFT JOIN derived_project_experience proj ON t.teacher_id = proj.teacher_id
                LEFT JOIN derived_research_area area ON t.teacher_id = area.teacher_id
                LEFT JOIN derived_email em ON t.teacher_id = em.teacher_id
                WHERE t.is_valid=1 AND (t.raw_data_id>={id_start} AND t.raw_data_id<={id_end});
                """
        return self.get_db(query)

    def get_paper_by_id_range(self, id_start, id_end):
        query = f"""
                SELECT id, author_list, addresses, affiliations, title, research_area, keywords, keywords_plus, email_addresses, reprint_addresses
                FROM raw_teacher_paper
                WHERE id >= {id_start} AND id <= {id_end};
                """
        return self.get_db(query)

    def process(self, input_data):
        """主处理流程"""

        merged_df = self.get_df(input_data["file"])

        if merged_df.empty:
            self.logger.debug("没有需要处理的数据")
            return

        merged_df = merged_df[merged_df["is_valid"] == 1]
        merged_df = merged_df.drop(columns=["orcid"]).copy()
        df_unique = merged_df.drop_duplicates(subset=["teacher_id", "paper_id"])

        sql = """
            INSERT IGNORE INTO product_teacher_paper_relation (teacher_id, paper_id, author_order, high_true, is_corresponding_author, is_valid)
            VALUES (:teacher_id, :paper_id, :author_order, :high_true, :is_corresponding_author, :is_valid);
            """

        # 更新数据
        self.logger.debug("开始插入数据库...")
        self.update_db(merged_df, sql)
