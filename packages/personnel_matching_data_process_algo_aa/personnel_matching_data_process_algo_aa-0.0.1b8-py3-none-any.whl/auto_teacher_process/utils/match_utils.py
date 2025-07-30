async def get_teacher_past_schools(db, teacher_id, school_name):
    """
    Get the past schools of a teacher.

    Args:
        db: Database connection object.
        teacher_id: ID of the teacher.

    Returns:
        List of past schools for the teacher.
    """
    query = f"""
        SELECT normalized_organization
        FROM derived_past_experience
        WHERE teacher_id = '{teacher_id}' AND is_valid = 1
    """
    school_df = await db.async_db_execute_query(query)
    past_schools_set = set() if school_df.empty else set(school_df["normalized_organization"].tolist())

    past_schools_set.add(school_name)  # 添加当前学校
    past_schools_cn_list = list(past_schools_set)

    return past_schools_cn_list


async def get_teacher_past_schools_by_teacher_ids(db, teacher_ids):
    # 删除数据
    teacher_ids_str = ",".join([f"'{i}'" for i in teacher_ids])

    query = f"""
        SELECT teacher_id, normalized_organization
        FROM derived_past_experience
        WHERE teacher_id IN ({teacher_ids_str}) AND is_valid = 1
    """
    school_df = await db.async_db_execute_query(query)

    return school_df


async def select_teacher_by_past_schools(db, teacher_df, school_names_cn):
    # 筛选出符合学校名称的教师
    # 如果school_name_cn为字符串，则将其转换为列表
    if isinstance(school_names_cn, str):
        school_names_cn = [school_names_cn]

    teacher_ids = teacher_df["teacher_id"].tolist()
    # 根据teacher_ids查询出这些教师的过往经历
    past_schools_df = await get_teacher_past_schools_by_teacher_ids(db=db, teacher_ids=teacher_ids)
    if past_schools_df is None or past_schools_df.empty:
        matched_teacher_ids = set()
    else:
        matched_teacher_ids = set(
            past_schools_df[past_schools_df["normalized_organization"].isin(school_names_cn)]["teacher_id"].tolist()
        )
    # 过滤出符合学校名称的教师
    matched_teacher_df = teacher_df[
        (teacher_df["teacher_id"].isin(matched_teacher_ids)) | (teacher_df["school_name"].isin(school_names_cn))
    ].copy()

    return matched_teacher_df
