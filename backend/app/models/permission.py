"""
楚然智考系统 - 权限定义模块
定义系统中所有权限编码
"""


class PermissionCode:
    """权限编码常量类"""
    
    # 用户管理权限
    USER_VIEW = "user:view"
    USER_CREATE = "user:create"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    
    # 角色管理权限
    ROLE_VIEW = "role:view"
    ROLE_CREATE = "role:create"
    ROLE_UPDATE = "role:update"
    ROLE_DELETE = "role:delete"
    
    # 题库管理权限
    QUESTION_VIEW = "question:view"
    QUESTION_CREATE = "question:create"
    QUESTION_UPDATE = "question:update"
    QUESTION_DELETE = "question:delete"
    QUESTION_IMPORT = "question:import"
    QUESTION_EXPORT = "question:export"
    
    # 知识点管理权限
    KNOWLEDGE_VIEW = "knowledge:view"
    KNOWLEDGE_CREATE = "knowledge:create"
    KNOWLEDGE_UPDATE = "knowledge:update"
    KNOWLEDGE_DELETE = "knowledge:delete"
    
    # 考试管理权限
    EXAM_VIEW = "exam:view"
    EXAM_CREATE = "exam:create"
    EXAM_UPDATE = "exam:update"
    EXAM_DELETE = "exam:delete"
    EXAM_PUBLISH = "exam:publish"
    EXAM_GRADE = "exam:grade"
    
    # 考试参与权限
    EXAM_TAKE = "exam:take"
    EXAM_REVIEW = "exam:review"
    
    # 统计分析权限
    STATS_VIEW = "stats:view"
    STATS_EXPORT = "stats:export"
    
    # 系统设置权限
    SYSTEM_CONFIG = "system:config"


# 默认角色权限配置
DEFAULT_ROLE_PERMISSIONS = {
    "admin": [
        # 管理员拥有所有权限
        PermissionCode.USER_VIEW, PermissionCode.USER_CREATE,
        PermissionCode.USER_UPDATE, PermissionCode.USER_DELETE,
        PermissionCode.ROLE_VIEW, PermissionCode.ROLE_CREATE,
        PermissionCode.ROLE_UPDATE, PermissionCode.ROLE_DELETE,
        PermissionCode.QUESTION_VIEW, PermissionCode.QUESTION_CREATE,
        PermissionCode.QUESTION_UPDATE, PermissionCode.QUESTION_DELETE,
        PermissionCode.QUESTION_IMPORT, PermissionCode.QUESTION_EXPORT,
        PermissionCode.KNOWLEDGE_VIEW, PermissionCode.KNOWLEDGE_CREATE,
        PermissionCode.KNOWLEDGE_UPDATE, PermissionCode.KNOWLEDGE_DELETE,
        PermissionCode.EXAM_VIEW, PermissionCode.EXAM_CREATE,
        PermissionCode.EXAM_UPDATE, PermissionCode.EXAM_DELETE,
        PermissionCode.EXAM_PUBLISH, PermissionCode.EXAM_GRADE,
        PermissionCode.EXAM_TAKE, PermissionCode.EXAM_REVIEW,
        PermissionCode.STATS_VIEW, PermissionCode.STATS_EXPORT,
        PermissionCode.SYSTEM_CONFIG,
    ],
    "student": [
        # 学员权限
        PermissionCode.QUESTION_VIEW,
        PermissionCode.KNOWLEDGE_VIEW,
        PermissionCode.EXAM_VIEW,
        PermissionCode.EXAM_TAKE,
        PermissionCode.EXAM_REVIEW,
        PermissionCode.STATS_VIEW,
    ]
}


# 权限描述
PERMISSION_DESCRIPTIONS = {
    PermissionCode.USER_VIEW: "查看用户",
    PermissionCode.USER_CREATE: "创建用户",
    PermissionCode.USER_UPDATE: "编辑用户",
    PermissionCode.USER_DELETE: "删除用户",
    PermissionCode.ROLE_VIEW: "查看角色",
    PermissionCode.ROLE_CREATE: "创建角色",
    PermissionCode.ROLE_UPDATE: "编辑角色",
    PermissionCode.ROLE_DELETE: "删除角色",
    PermissionCode.QUESTION_VIEW: "查看题目",
    PermissionCode.QUESTION_CREATE: "创建题目",
    PermissionCode.QUESTION_UPDATE: "编辑题目",
    PermissionCode.QUESTION_DELETE: "删除题目",
    PermissionCode.QUESTION_IMPORT: "导入题库",
    PermissionCode.QUESTION_EXPORT: "导出题库",
    PermissionCode.KNOWLEDGE_VIEW: "查看知识点",
    PermissionCode.KNOWLEDGE_CREATE: "创建知识点",
    PermissionCode.KNOWLEDGE_UPDATE: "编辑知识点",
    PermissionCode.KNOWLEDGE_DELETE: "删除知识点",
    PermissionCode.EXAM_VIEW: "查看考试",
    PermissionCode.EXAM_CREATE: "创建考试",
    PermissionCode.EXAM_UPDATE: "编辑考试",
    PermissionCode.EXAM_DELETE: "删除考试",
    PermissionCode.EXAM_PUBLISH: "发布考试",
    PermissionCode.EXAM_GRADE: "考试判分",
    PermissionCode.EXAM_TAKE: "参加考试",
    PermissionCode.EXAM_REVIEW: "查看考试解析",
    PermissionCode.STATS_VIEW: "查看统计",
    PermissionCode.STATS_EXPORT: "导出统计",
    PermissionCode.SYSTEM_CONFIG: "系统配置",
}
