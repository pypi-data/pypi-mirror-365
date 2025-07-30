from .common import (
    get_raw_string,
    get_line_option,
    Path,
    get_line_option_as_bool,
    get_line_option_as_int,
)
import logging


class ProgramConfigV2:
    hospital_config_dir: Path = None

    @classmethod
    def set_hospital_config_dir(cls, config_dir: Path):
        cls.hospital_config_dir = config_dir

    @classmethod
    def get_config(cls, file_relative_path: str):
        if cls.hospital_config_dir is None:
            logging.warning(f'医院配置目录未设置，使用当前目录{Path.cwd()}')
            cls.hospital_config_dir = Path.cwd()
        return cls.hospital_config_dir.joinpath(file_relative_path)

    @classmethod
    def get_url(cls):
        return get_raw_string(cls.get_config('文档/admin.txt'), 1)

    @classmethod
    def get_username(cls):
        return get_raw_string(cls.get_config('文档/admin.txt'), 2)

    @classmethod
    def get_password(cls):
        return get_raw_string(cls.get_config('文档/admin.txt'), 3)

    @classmethod
    def get_department_name(cls):
        return get_raw_string(cls.get_config('文档/admin.txt'), 4)

    @classmethod
    def get_follow_up_start_date(cls):
        return get_line_option(cls.get_config('文档/admin.txt'), '随访新建起始时间')

    @classmethod
    def get_follow_up_end_date(cls):
        return get_line_option(cls.get_config('文档/admin.txt'), '随访新建结束时间')

    @classmethod
    def get_completed_count(cls):
        return get_line_option_as_int(cls.get_config('执行结果/env.txt'), '已完成数量')

    @classmethod
    def get_organization_name(cls):
        return get_line_option(cls.get_config('执行结果/env.txt'), '机构名称')

    @classmethod
    def use_other_doctor_records(cls) -> bool:
        # 没有签约医生的门诊记录, 是否需要判别包含机构名称字样的其他医生的门诊记录
        return get_line_option_as_bool(
            cls.get_config('执行结果/env.txt'), '没有签约医生的门诊'
        )

    @classmethod
    def continue_save_if_already_done_test(cls) -> bool:
        # 本季度已做过慢病随访，是否继续保存
        return get_line_option_as_bool(
            cls.get_config('执行结果/env.txt'), '本季度已做过慢病随访，是否继续保存'
        )

    @classmethod
    def no_diabetes_record_fasting_blood_sugar(cls) -> bool:
        # 无糖尿病是否录入空腹血糖
        return get_line_option_as_bool(
            cls.get_config('执行结果/env.txt'), '无糖尿病是否录入空腹血糖'
        )

    @classmethod
    def introduction_medication_start_date(cls):
        # 引入用药起始时间
        return get_line_option(cls.get_config('执行结果/env.txt'), '引入用药起始时间')

    @classmethod
    def introduction_medication_end_date(cls):
        # 引入用药结束时间
        return get_line_option(cls.get_config('执行结果/env.txt'), '引入用药结束时间')
