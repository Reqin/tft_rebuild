from modules.creations.Equipment import Equipment
from modules.log.log import log
from modules.filePipe.pipe import pklDump, pklLoad
import inspect


# 角色姓名类
# 通过设置姓名来进行数据的自动装载
class Name(str):
    def __init__(self, value=''):
        self.value = value
        pass

    def __get__(self, instance, owner):
        return self.value

    def __set__(self, instance, value):
        self.value = value
        if instance.resource == {}:
            return
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
                    attrValue = instance.resource[self.value].__getattribute__(
                        instanceAttrName)
                    attr.__set__(instance, attrValue)
                except:
                    log(" failed to set character attr :" + str(instanceAttrName))


# 角色头像类


class HeaderImg:
    def __init__(self, value=[]):
        self.value = value

    def __get__(self, instance, owner):
        return self.value

    def __set__(self, instance, value):
        self.value = value


# 角色图片类
class CharacterImg:
    def __init__(self, value=[]):
        self.value = value

    def __get__(self, instance, owner):
        return self.value

    def __set__(self, instance, value):
        self.value = value


# 角色装备区类
class EquipmentArea:

    def __init__(self):
        # 装备区最大面积
        self.maxArea = 3
        # 装备区剩余面积
        self.residualArea = 3
        # 装备控制字
        self.equipments = {}

    def __get__(self, instance, owner):
        return self

    # 获取全部装备
    def all(self):
        return self.equipments

    # 检查装备
    def checkEquipment(self, equipment):
        if isinstance(equipment, Equipment):
            return True
        else:
            log(" 错误的装备类型 ")
            return False

    # 放置装备
    def place(self, equipment, location):
        if not self.checkEquipment(equipment):
            return False
        if location in self.equipments.keys():
            return False
        if equipment.area > self.residualArea:
            return False
        self.equipments[location] = equipment
        self.residualArea = self.residualArea - equipment.area
        return True

    # 移除装备
    def remove(self, location):
        # 空的装备区
        if location not in self.equipments.keys():
            return True
        try:
            self.residualArea = self.residualArea + \
                                self.equipments[location].area
            del self.equipments[location]
        except:
            log(" 移除装备时发生错误 ")
            return False
        return True

    # 替换装备
    def replace(self, equipment, location):
        if self.remove(location):
            if self.place(equipment, location):
                return True
        return False

    # 移除所有装备
    def removeAll(self):
        self.equipments = {}
        self.residualArea = self.maxArea


class Character:
    def __init__(self):
        self.name = Name()
        self.equipmentArea = EquipmentArea()
        self.headerImg = HeaderImg()
        self.characterImg = CharacterImg()
        self.resource = {}

    def __getattr__(self, name):
        info = ' character attr ' + name + ' is not an Initialization '
        log(info)
        raise AttributeError(info)

    def checkCharacter(self, character):
        if not isinstance(character, Character):
            log(" 错误的角色数据 ")
            return False
        return True

    def getAlly(self, character):
        flag = self.checkCharacter(character)
        if flag:
            if character.name in self.resource.keys():
                log(" 尝试重复加入盟友 ")
                flag = False
            else:
                self.resource[character.name] = character
                flag = True
        return flag

    def loseAlly(self, character):
        flag = self.checkCharacter(character)
        if flag:
            if character.name not in self.resource.keys():
                log(" 尝试移除不存在的盟友 ")
                flag = False
            else:
                del self.resource[character.name]
                flag = True
        return flag

    def placeEquipment(self, equipment, location):
        return self.equipmentArea.place(equipment, location)

    def removeEquipment(self, location):
        return self.equipmentArea.remove(location)

    def replaceEquipment(self, equipment, location):
        return self.equipmentArea.replace(equipment, location)


def loadCharacterHandle(path):
    try:
        characterHandle = Character()
        charactersData = pklLoad(path)
        # TODO
        # 不使用循环进行自动属性赋值是为了更好的修改
        for characterData in charactersData.values():
            character = Character()
            character.name = characterData["name"]
            character.headerImg = characterData["headerImg"]
            character.characterImg = characterData["characterImg"]
            character.equipmentArea.equipments = characterData['equipmentArea']["equipments"]
            characterHandle.getAlly(character)
        return characterHandle
    except Exception:
        log(" 载入数据出错 path:" + str(path))
        return False


def dumpCharacterHandle(characterHandle, path):
    try:
        charactersData = {}
        for character in characterHandle.resource.values():
            characterData = {}
            characterData['name'] = character.name
            characterData['headerImg'] = character.headerImg
            characterData['characterImg'] = character.characterImg
            characterData['equipmentArea'] = {}
            characterData['equipmentArea']["equipments"] = character.equipmentArea.equipments
            charactersData[character.name] = characterData
        pklDump(charactersData, path)
        return True
    except:
        log(" 导出数据出错 path:" + str(path))
        return False
