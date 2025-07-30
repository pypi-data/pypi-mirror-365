def extract_matched_schools_from_applicant(applicant: str, school_cn_list: list[str]) -> list[str]:
    """
    从学校中文名列表中筛选出出现在 applicant 字段中的学校
    Args:
        applicant: 专利申请人字符串
        school_cn_list: 全部学校中文名列表

    Returns:
        匹配到的学校列表（去重，保持顺序）
    """
    if not applicant:
        return []

    matched_schools = []
    for school in school_cn_list:
        if school in applicant:
            matched_schools.append(school)

    # 去重（如果 applicant 出现多次）
    return list(dict.fromkeys(matched_schools))  # 保留顺序
