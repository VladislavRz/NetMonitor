from enum import Enum


class Tags(Enum):
    add_h = 'NewHost'
    delete_h = 'DeleteHost'
    open_p = 'OpenPort'
    close_p = 'ClosePort'
    change_p = 'ChangePortStatus'


ivre_url = '127.0.0.1'
hive_url = 'http://127.0.0.1:9000'
hive_api_key = 'd+5b7fWaXvBACElTB7XwTwAhMAgg4+24'
