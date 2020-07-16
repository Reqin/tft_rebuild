from modules.log.log import log
import inspect
import os
import types


# 装备名类
class Name(str):
    def __init__(self, value=''):
        self.value = value
        pass

    def __get__(self, instance, owner):
        return self.value

    def __set__(self, instance, value):
        self.value = value
        # 更新character实例
        instanceAttrsName = dir(instance)
        for instanceAttrName in instanceAttrsName:
            if not instanceAttrName[0].startswith('_'):
                attr = inspect.getattr_static(instance, instanceAttrName)
                # IMPORTANT 避免递归，一定不能删
                if attr is self:
                    break
                # 是否为函数
                if hasattr(attr, "__call__"):
                    continue
                # 是否为自身资源
                if instanceAttrName == "resource":
                    continue
                try:
                    for i in range(len(instance.resource)):
                        if instance.resource[i].name == self.value:
                            attrValue = instance.resource[i].__getattribute__(
                                instanceAttrName)
                            attr.__set__(self, attrValue)
                except:
                    log(" failed to set equipment attr :" + str(instanceAttrName))


# 装备图片类
class EquipmentImg:
    def __init__(self, value=[]):
        self.value = value

    def __get__(self, instance, owner):
        return self.value

    def __set__(self, instance, value):
        self.value = value


# 装备占用类
class Area:
    def __init__(self, value=[]):
        self.value = value

    def __get__(self, instance, owner):
        return self.value

    def __set__(self, instance, value):
        self.value = value


# 装备类
class Equipment:
    

    def __init__(self):
        self.name = Name()
        self.equipmentImg = EquipmentImg()
        self.area = Area()
        self.resource = {}

    def __getattr__(self, name):
        info = ' Equipment attr ' + name + ' is not an Initialization '
        log(info)
        raise AttributeError(info)

    def checkEquipment(self, equipment):
        if not isinstance(equipment, Equipment):
            log(" 错误的装备数据 ")
            return False
        return True

    def getAlly(self, equipment):
        state = self.checkEquipment(equipment)
        if state:
            self.resource[equipment.name] = equipment
        return state

    def loseAlly(self, equipment):
        state = self.checkEquipment(equipment)
        if state:
            for i in range(len(self.resource)):
                if equipment.name in self.resource.keys():
                    del self.resource[i]
                    return True
        log(" 尝试移除不存在的盟友 ")
        return False

    def getEquipment(self, equipment):
        return self.equipmentArea.place(equipment)

    def loseEquipment(self, equipment):
        return self.equipmentArea.remove(equipment)


def loadEquipmentsHandle(path):
    from modules.filePipe.pipe import pklLoad
    equipmentHandle = Equipment()
    try:
        equipmentsData = pklLoad(path)
        for equipmentData in equipmentsData:
            equipment = Equipment()
            equipment.name = equipmentData["name"]
            equipment.equipmentImg = equipmentData["equipmentImg"]
            equipment.area = equipmentData["area"]
            equipmentHandle.getAlly(equipment)
    except:
        log(" 载入数据出错 path:" + str(path))
    finally:
        return equipmentHandle

def getEquipmentsNames(equipmentHandle):
    names = []
    for equipment in equipmentHandle.resource:
        names.append(equipment.name)
    return names
