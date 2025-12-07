-- 进入目标数据库
USE `system`;

-- ========================
-- 1. exams 表结构调整
-- ========================

-- 1.1 duration 字段：允许 0 表示不限时（如果你之前已经是 INT 可执行下面语句）
ALTER TABLE `exams`
  MODIFY COLUMN `duration` INT DEFAULT 120 COMMENT '考试时长(分钟)，0表示不限时';

-- 1.2 新增随机抽题数量字段
ALTER TABLE `exams`
  ADD COLUMN `random_question_count` INT NOT NULL DEFAULT 0
    COMMENT '随机抽题数量，0表示不使用统一随机数量'
    AFTER `random_config`;

-- 1.3 新增题型过滤字段：all/single/multiple
ALTER TABLE `exams`
  ADD COLUMN `question_type_filter` VARCHAR(20) NOT NULL DEFAULT 'all'
    COMMENT '题型过滤: all/single/multiple'
    AFTER `random_question_count`;


-- ========================
-- 2. 新建考试-题库关联表
--    exam_question_banks
-- ========================

CREATE TABLE IF NOT EXISTS `exam_question_banks` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `exam_id` INT NOT NULL COMMENT '考试ID',
  `bank_id` INT NOT NULL COMMENT '题库ID',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_exam_bank` (`exam_id`, `bank_id`),
  CONSTRAINT `fk_eqb_exam`
    FOREIGN KEY (`exam_id`) REFERENCES `exams` (`id`)
    ON DELETE CASCADE,
  CONSTRAINT `fk_eqb_bank`
    FOREIGN KEY (`bank_id`) REFERENCES `question_banks` (`id`)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='考试与题库关联表';