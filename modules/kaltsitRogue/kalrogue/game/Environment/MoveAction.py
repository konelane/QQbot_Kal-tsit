class MoveAction:
    """
        用于返回node执行信息

    """
    # 返回文本
    __outtext: str = ''
    # 消息类型
    __extra_msg_type: str = 'auto'
    # 下一节点名称
    __node_name: str = None
    # 有无额外信息 标志 若为false则正常进行
    __extra_flag: bool = False

    # 检查状态 NOT_CHECK CHECKED PASSED
    __check_status: str = "NOT_CHECK"

    def __init__(self):
        pass


    def get_outtext(self):
        return self.__outtext

    def set_outtext(self, outtext: str):
        self.__outtext = outtext

    def get_extra_msg_type(self):
        return self.__extra_msg_type

    def set_extra_msg_type(self, extra_msg_type: str):
        self.__extra_msg_type = extra_msg_type

    def get_node_name(self):
        return self.__node_name

    def set_node_name(self, node_name: str):
        self.__node_name = node_name

    def if_extra_flag(self):
        return self.__extra_flag

    def set_extra_flag(self, extra_flag: bool):
        self.__extra_flag = extra_flag

    def get_check_status(self):
        return self.__check_status

    def set_check_status(self, check_status: str):
        self.__check_status = check_status
