from calculators.calc_dispatcher.ui_interface import start_app
from infrastructure_path_utils import get_root_dir_path

dispatcher_calc_path = get_root_dir_path() / "calculators" / "calc_dispatcher"

start_app(directory=dispatcher_calc_path)
