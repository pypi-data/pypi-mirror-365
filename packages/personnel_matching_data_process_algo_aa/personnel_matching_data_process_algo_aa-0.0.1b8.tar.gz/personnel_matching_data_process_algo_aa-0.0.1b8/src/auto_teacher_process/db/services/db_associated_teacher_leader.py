from auto_teacher_process.db.db_base import BaseDBProcessor


class TeacherLeaderAssociatedProcessor(BaseDBProcessor):
    """领导老师关联"""

    def get_teacher_leader_group(self, school_name: str):
        query = f"""
        SELECT 
            l.teacher_name AS name,
            l.school_name,
            l.id AS leader_id,
            t.teacher_id,
            l.description AS leader_description,
            t.description AS teacher_description
        FROM 
            raw_leaders_data l
        INNER JOIN 
            derived_teacher_data t
        ON 
            l.school_name = t.school_name
            AND l.teacher_name = t.derived_teacher_name
            AND t.is_valid = 1
        WHERE
            l.school_name = '{school_name}';
        """
        return self.get_db(query)

    def process(self, input_data):
        return super().process(input_data)
