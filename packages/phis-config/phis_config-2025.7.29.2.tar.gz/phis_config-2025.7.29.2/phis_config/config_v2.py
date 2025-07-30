from .common import Path
import logging
from .config_class import PhisConfig


_singleton_instance: PhisConfig | None = None


def _get_instance() -> PhisConfig:
    global _singleton_instance
    if _singleton_instance is None:
        logging.warning(f'医院配置目录未设置，使用当前目录{Path.cwd()}')
        _singleton_instance = PhisConfig(Path.cwd())
    return _singleton_instance


class ProgramConfigV2:
    @classmethod
    def set_hospital_config_dir(cls, config_dir: Path):
        global _singleton_instance
        _singleton_instance = PhisConfig(config_dir)

    @classmethod
    def get_config(cls, file_relative_path: str):
        return _get_instance().get_config(file_relative_path)

    @classmethod
    def get_url(cls):
        return _get_instance().get_url()

    @classmethod
    def get_username(cls):
        return _get_instance().get_username()

    @classmethod
    def get_password(cls):
        return _get_instance().get_password()

    @classmethod
    def get_department_name(cls):
        return _get_instance().get_department_name()

    @classmethod
    def get_follow_up_start_date(cls):
        return _get_instance().get_follow_up_start_date()

    @classmethod
    def get_follow_up_end_date(cls):
        return _get_instance().get_follow_up_end_date()

    @classmethod
    def get_completed_count(cls):
        return _get_instance().get_completed_count()

    @classmethod
    def get_organization_name(cls):
        return _get_instance().get_organization_name()

    @classmethod
    def use_other_doctor_records(cls) -> bool:
        return _get_instance().use_other_doctor_records()

    @classmethod
    def continue_save_if_already_done_test(cls) -> bool:
        return _get_instance().continue_save_if_already_done_test()

    @classmethod
    def no_diabetes_record_fasting_blood_sugar(cls) -> bool:
        return _get_instance().no_diabetes_record_fasting_blood_sugar()

    @classmethod
    def introduction_medication_start_date(cls):
        return _get_instance().introduction_medication_start_date()

    @classmethod
    def introduction_medication_end_date(cls):
        return _get_instance().introduction_medication_end_date()
