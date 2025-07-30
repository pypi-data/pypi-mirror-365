from time import time
from warnings import warn

import numpy as np
from pandas import DataFrame

from .HandData.OneHand import OneHand
from .HandData.Gestrue import Gestrue
from .HandData._global import HAND_DATA_COL_NAME
from .HandDetector.VisualHandDetector import VisualHandDetector
from .HandDetector.MediaPipeHandDetector import MediaPipeHandDetector
from .HandDetector.HandsMatchers import HandsMatcher, HungarianMatcher
from .HandUtils.Drawing import HandDrawing
from .HandInputSchemes.HandInputScheme import HandInputScheme


class BaseHandAPI:
    __slots__ = "one_hand", "delta_time"

    def __init__(self, one_hand: OneHand) -> None:
        self.one_hand: OneHand = one_hand
        # 记录帧间时间,初始值为1
        self.delta_time: float = 1

    def hand_side(self) -> str:
        """获取该手部是左手还是右手"""
        return self.one_hand.hand_side

    def img_pos(self, point_id: int = -1) -> np.ndarray:
        """获取该手部的第point_id个关键点在图片中的像素坐标
        Args:
            point_id: 关键点编号;默认值-1返回所有关键点的像素坐标
        """
        if 20 >= point_id >= 0:  # 返回指定关键点的像素坐标的副本
            return self.one_hand.raw_pos[point_id, :2].astype(np.int32)
        elif point_id == -1:  # 返回所有关键点的像素坐标的副本
            return self.one_hand.raw_pos[:, :2].astype(np.int32)
        raise ValueError(f"No coordinate data with point_id {point_id}")

    def norm_pos(self, point_id: int = -1, copy: bool = True) -> np.ndarray:
        """获取该手部的索引为point_id的以手部矩形框左上角为原点的归一化xyz坐标
        Args:
            point_id: 关键点编号;默认值-1返回所有关键点的归一化坐标
            copy: 是否返回副本,默认为True返回副本,注意:若为False,请不要修改该值,这是只读的
        """
        if 20 >= point_id >= 0:  # 返回指定的关键点归一化坐标
            output = self.one_hand.norm_pos[point_id, :]
        elif point_id == -1:  # 返回该手部所有的关键点的归一化坐标
            output = self.one_hand.norm_pos
        else:
            raise ValueError(f"There is no coordinate data with point_id {point_id}")
        # 返回nrom_pos的副本,防止原来的数据被修改
        return output.copy() if copy else output

    def wrist_npos(self, point_id: int = -1, copy: bool = True) -> np.ndarray:
        """获取该手部的索引为point_id的以手腕为原点的归一化xyz坐标
        Args:
            point_id: 关键点编号;默认值-1返回所有关键点的以手腕为原点的归一化坐标
            copy: 是否返回副本,默认为True返回副本,注意:若为False,请不要修改该值,这是只读的
        """
        if 20 >= point_id > 0:  # 返回指定的关键点归一化坐标
            output = self.one_hand.wrist_npos[point_id, :]
        elif point_id == -1:  # 返回该手部所有的关键点的归一化坐标
            output = self.one_hand.wrist_npos
        elif point_id == 0:  # 以手腕坐标为原点,直接返回原点坐标000
            return np.array([0, 0, 0], dtype=np.float32)
        else:
            raise ValueError(f"There is no coordinate data with point_id {point_id}")
        return output.copy() if copy else output

    def norm2img_pos(
        self,
        point_id: int = -1,
        img_size: tuple[int, int] = (100, 100),
        padding: tuple[int, int] = (0, 0),
    ) -> np.ndarray:
        """将归一化后的坐标转换为特定大小的图片位置坐标,返回坐标数组
        Args:
            point_id: 该手部的关键点编号
            img_size: 转换的图片尺寸,(图片宽,图片高)
            padding: 图片周围的间隔距离,(padx,pady)
        """
        if point_id > 20 or point_id < -1:
            raise ValueError(f"There is no coordinate data with point_id {point_id}")
        # 获取对应手部的关键点坐标
        npos = (
            self.one_hand.norm_pos[point_id, :2]
            if 20 >= point_id >= 0
            else self.one_hand.norm_pos[:, :2]
        )
        img_size_arr = np.array(img_size[::-1])
        padding_arr = np.array(padding)
        # 计算转换后的图片坐标
        ipos = (npos * (img_size_arr - (2 * padding_arr))) + padding_arr
        return ipos.astype(np.int32)

    def box(self) -> np.ndarray:
        """获取对应名字的手部最小矩形框的在图片中的xyxy像素坐标"""
        return self.one_hand.box

    def finger_angle(self, point_id: int = -1, copy: bool = True) -> np.ndarray:
        """获取对应名字的手部关键点弧度制角度,其中指尖和手腕没有角度数据
        Args:
            point_id: 关键点编号;默认值-1返回所有手指关节点角度数据
            copy: 是否返回副本,默认为True返回副本,注意:若为False,请不要修改该值,这是只读的
        """
        finger_id, angle_id = divmod(point_id, 4)  # 计算关键点对应的角度数组中的索引
        if 20 >= point_id > 0 and angle_id != 0:  # 指尖和手腕没有角度数据
            output = self.one_hand.fingers_angle[finger_id, (angle_id - 1)]
        elif point_id == -1:  # 没有输入point_id则返回全部角度
            output = self.one_hand.fingers_angle
        else:
            raise ValueError(f"There is no angle data with point_id {point_id}")
        return output.copy() if copy else output

    def thumb_dist(self, other_point_id: int = -1, copy: bool = True) -> np.ndarray:
        """获取对应名字的手部的从大拇指到其他手指关键点的曼哈顿距离
        Args:
            point_id: 关键点编号;默认值-1返回4根指尖到大拇指指尖的距离
            copy: 是否返回副本,默认为True返回副本,注意:若为False,请不要修改该值,这是只读的
        """
        if other_point_id in (8, 12, 16, 20):
            # 计算对应的数组的索引
            finger_id, knuckle_id = divmod(other_point_id, 4)
            arr_id = (knuckle_id - 1) if knuckle_id != 0 else (finger_id + 1)
            output = self.one_hand.thumb_dist[arr_id]
        elif other_point_id == -1:  # 没有输入id则返回全部到拇指的距离
            output = self.one_hand.thumb_dist
        else:
            raise ValueError(
                f"There is no distance data with point_id {other_point_id}"
            )
        return output.copy() if copy else output

    def wrist_npos_velocity(self, point_id: int = -1) -> np.ndarray:
        """获取该手部的第point_id个关键点两帧之间的归一化坐标差值
        Args:
            point_id: 关键点编号,默认值-1则返回所有两帧差坐标
        """
        if 20 >= point_id >= 0:  # 返回指定关键点的两帧像素差坐标
            return self.one_hand.wrist_npos_diff[point_id] / self.delta_time
        elif point_id == -1:  # 返回所有关键点的两帧像素差坐标
            return self.one_hand.wrist_npos_diff / self.delta_time
        raise ValueError(f"There is no coordinate data with point_id {point_id}")

    def angle_velocity(self, point_id: int = -1) -> np.ndarray:
        """获取对应名字的手部关键点弧度制角度差,其中指尖和手腕没有角度数据
        Args:
            point_id: 关键点编号,默认值-1则返回所有角度差
        """
        finger_id, angle_id = divmod(point_id, 4)  # 计算关键点对应的角度数组中的索引
        if 20 >= point_id > 0 and angle_id != 0:  # 指尖和手腕没有角度数据
            return self.one_hand.angle_diff[finger_id, (angle_id - 1)] / self.delta_time
        elif point_id == -1:  # 没有输入point_id则返回全部角度差
            return self.one_hand.angle_diff / self.delta_time
        raise ValueError(f"There is no angle data with point_id {point_id}")


class HandDataAPI:
    __slots__ = "one_hand"

    def __init__(self, one_hand: OneHand) -> None:
        self.one_hand: OneHand = one_hand

    @property
    def norm_pos(self) -> np.ndarray:
        """获取对应名字的手部的所有连续型数据的数组"""
        return self.one_hand.pos_data

    @property
    def norm_pos2DataFrame(self) -> DataFrame:
        """获取对应名字的手部的所有连续型数据的DataFrame格式的数据"""
        return DataFrame(self.one_hand.pos_data, columns=HAND_DATA_COL_NAME.iloc[:63])

    @property
    def finger(self) -> np.ndarray:
        """获取对应名字的手部的手指角度和指尖距离数据的数组"""
        return self.one_hand.finger_data

    @property
    def finger2DataFrame(self) -> DataFrame:
        """获取对应名字的手部的手指角度和指尖距离数据的DataFrame格式的数据"""
        return DataFrame(
            self.one_hand.finger_data, columns=HAND_DATA_COL_NAME.iloc[63:]
        )

    @property
    def all_data(self) -> np.ndarray:
        """获取对应名字的手部的所有连续型数据的数组"""
        return self.one_hand.data

    @property
    def all2DataFrame(self) -> DataFrame:
        """获取对应名字的手部的所有连续型数据的DataFrame格式的数据"""
        return DataFrame(self.one_hand.data, columns=HAND_DATA_COL_NAME)


class HandAPI:
    __slots__ = "_base", "_data", "_gestrue", "_drawing"

    def __init__(self, one_hand: OneHand):
        """用于管理一只手部的所有相关数据和模型
        Args:
            one_hand: 输入该手部的基础数据类实例
        """
        self._base: BaseHandAPI = BaseHandAPI(one_hand)
        self._data: HandDataAPI = HandDataAPI(one_hand)
        self._gestrue: Gestrue = Gestrue(one_hand)
        self._drawing: HandDrawing = HandDrawing(one_hand)

    @property
    def base(self) -> BaseHandAPI:
        """返回该手部的基本手部数据的API"""
        return self._base

    @property
    def data(self) -> HandDataAPI:
        """返回该手部的一维数据格式的手部数据的API"""
        return self._data

    @property
    def gestrue(self) -> Gestrue:
        """返回该手部的手指状态相关数据的API"""
        return self._gestrue

    @property
    def drawing(self) -> HandDrawing:
        """返回绘制手部相关的API"""
        return self._drawing


class HandInput:
    __slots__ = (
        "hands_dict",
        "one_hand_dict",
        "detector",
        "detected_name_ls",
        "frame",
        "_last_frame_time",
        "_delta_time",
        "schemes",
    )

    def __init__(
        self,
        hands_name_ls: list[str],
        hands_detector: type[VisualHandDetector] = MediaPipeHandDetector,
        hands_matcher: type[HandsMatcher] = HungarianMatcher,
        **detector_kwargs,
    ) -> None:
        # 手部数据字典用作手部检测的参数
        self.one_hand_dict: dict[str, OneHand] = {
            name: OneHand() for name in hands_name_ls
        }
        # 利用传入的手部名字来创建对应的手部API字典
        self.hands_dict: dict[str, HandAPI] = {
            name: HandAPI(ohand) for name, ohand in self.one_hand_dict.items()
        }
        # 根据传入的检测器类创建视觉手部检测器实例,添加手部名字列表的数量参数
        detector_kwargs["hands_name_ls"] = hands_name_ls
        detector_kwargs["hands_matcher"] = hands_matcher
        self.detector: VisualHandDetector = hands_detector(**detector_kwargs)
        # 创建一个用于记录本次检测到的手部的名称的列表
        self.detected_name_ls: list[str] = []
        # 记录每帧的图像
        self.frame: None | np.ndarray = None
        # 记录两帧之间的间隔时间,初始值为1
        self._last_frame_time: float = time()
        self._delta_time: float = 1
        # 创建存放手部操控方案的字典
        self.schemes: dict[str, HandInputScheme] = dict()

    def __repr__(self) -> str:
        return f"skhand.HandInput(\n\thands={list(self.hands_dict.keys())}, \n\tdetector={self.detector}, \n\tschemes={self.schemes}\n)"

    def __str__(self) -> str:
        return f"HandInput(\n\thands={list(self.hands_dict.keys())}, \n\tdetector={self.detector}, \n\tschemes={self.schemes}\n)"

    def run(self, frame: np.ndarray) -> list[str]:
        """运行手部关键点检测器,返回成功检测到的手部名称
        Args:
            frame: 输入需要检测的帧图像
        """
        self.frame = frame  # 记录帧图像变量
        # 检测并更新手部数据
        self.detected_name_ls = self.detector.detect(frame, self.one_hand_dict)
        # 更新帧间时间
        cur_frame_time = time()
        self._delta_time = cur_frame_time - self._last_frame_time
        self._last_frame_time = cur_frame_time
        # 实时更新手部操控方案
        for scheme in self.schemes.values():
            scheme.update()
        return self.detected_name_ls

    @property
    def delta_time(self) -> float:
        """返回两帧之间的间隔时间,初始值为1"""
        return self._delta_time

    def __getitem__(self, hand_name: str) -> HandAPI:
        """指定相应的手部,返回对应手部的API,没有检测到就抛出错误
        Args:
            hand_name: 当前检测到的手部名字
        """
        # 检查指定的手部是否有检测到
        if hand_name not in self.detected_name_ls:
            raise KeyError(f"Hand named '{hand_name}' was not detected")
        hand = self.hands_dict[hand_name]
        hand.base.delta_time = self.delta_time  # 更新帧间时间
        hand.drawing.raw_img = self.frame  # 设定原始图像
        return hand

    def hand(self, hand_name: str) -> HandAPI | None:
        """指定相应的手部,返回对应手部的API,没有检测到的返回None
        Args:
            hand_name: 当前检测到的手部名字,没有检测到则返回None
        """
        # 检查指定的手部是否有检测到
        if hand_name not in self.detected_name_ls:
            return None
        return self.hands_dict[hand_name]

    def base(self, hand_name: str) -> BaseHandAPI | None:
        """获取基础的手部数据,没有检测到的返回None
        Args:
            hand_name: 当前检测到的手部名字,没有检测到则返回None
        """
        hand = self.hand(hand_name)
        if hand is None:
            return None
        hand.base.delta_time = self.delta_time  # 更新帧间时间
        return hand.base

    def data(self, hand_name: str) -> HandDataAPI | None:
        """获取一维的手部相关数据,没有检测到的返回None
        Args:
            hand_name: 当前检测到的手部名字,没有检测到则返回None
        """
        hand = self.hand(hand_name)
        if hand is None:
            return None
        return hand.data

    def gestrue(self, hand_name: str) -> Gestrue | None:
        """获取手势相关数据,没有检测到的返回None
        Args:
            hand_name: 当前检测到的手部名字,没有检测到则返回None
        """
        hand = self.hand(hand_name)
        if hand is None:
            return None
        return hand.gestrue

    def drawing(self, hand_name: str) -> HandDrawing | None:
        """获取手部绘制工具,没有检测到的返回None
        Args:
            hand_name: 当前检测到的手部名字,没有检测到则返回None
        """
        hand = self.hand(hand_name)
        if hand is None:
            return None
        hand.drawing.raw_img = self.frame  # 设定原始图像
        return hand.drawing

    def add_scheme(
        self, hand_name: str, scheme_name: str, new_scheme: type[HandInputScheme]
    ):
        """用默认参数来添加新的手部操控方案
        Args:
            hand_name: 当前检测到的手部名字,没有该手部名字则报错
            scheme_name: 设置新增的手部操控方案的名字
            scheme: 输入手部操控方案实例,创建时需设置好参数
        """
        if hand_name not in self.hands_dict.keys():
            raise KeyError(f"Hand named '{hand_name}' is not exist")
        # 使用默认参数来添加新的手部操控方案
        self.schemes[scheme_name] = new_scheme(self, hand_name)

    """以下是已经弃用的函数"""

    def hand_unwrap(self, hand_name: str) -> HandAPI:
        """指定相应的手部,返回对应手部的API,没有检测到就抛出错误
        Args:
            hand_name: 当前检测到的手部名字,没有检测到则报错
        """
        # 检查指定的手部是否有检测到
        warn(
            "hand_unwrap is deprecated, you can use `HandInput[hand_name].hand` instead.",
            category=DeprecationWarning,
        )
        if hand_name not in self.detected_name_ls:
            raise ValueError(f"No hand named '{hand_name}' was detected")
        return self.hands_dict[hand_name]

    def base_unwrap(self, hand_name: str) -> BaseHandAPI:
        """获取基础的手部数据,没有检测到就抛出错误
        Args:
            hand_name: 当前检测到的手部名字,没有检测到则报错
        """
        warn(
            "base_unwrap is deprecated, you can use `HandInput[hand_name].base` instead.",
            category=DeprecationWarning,
        )
        hand = self.hand_unwrap(hand_name)
        hand.base.delta_time = self.delta_time  # 设定时间间隔
        return hand.base

    def data_unwrap(self, hand_name: str) -> HandDataAPI:
        """获取一维的手部相关数据,没有检测到就抛出错误
        Args:
            hand_name: 当前检测到的手部名字,没有检测到则报错
        """
        warn(
            "data_unwrap is deprecated, you can use `HandInput[hand_name].data` instead.",
            category=DeprecationWarning,
        )
        return self.hand_unwrap(hand_name).data

    def gestrue_unwrap(self, hand_name: str) -> Gestrue:
        """获取手势相关数据,没有检测到就抛出错误
        Args:
            hand_name: 当前检测到的手部名字,没有检测到则报错
        """
        warn(
            "gestrue_unwrap is deprecated, you can use `HandInput[hand_name].gestrue` instead.",
            category=DeprecationWarning,
        )
        return self.hand_unwrap(hand_name).gestrue

    def drawing_unwrap(self, hand_name: str) -> HandDrawing:
        """获取手部绘制工具,没有检测到就抛出错误
        Args:
            hand_name: 当前检测到的手部名字,没有检测到则报错
        """
        warn(
            "drawing_unwrap is deprecated, you can use `HandInput[hand_name].drawing` instead.",
            category=DeprecationWarning,
        )
        hand = self.hand_unwrap(hand_name)
        hand.drawing.raw_img = self.frame  # 设定原始图像
        return hand.drawing
