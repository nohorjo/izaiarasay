def getPropertyFromFile(confFileName, propName, multiple=False):
    confFile = open(confFileName)
    rtn = getPropertyFromList(confFile.readlines(), propName, multiple)
    confFile.close()
    return rtn


def getPropertyFromList(propertyList, propName, multiple=False):
    rtnProps = []
    for prop in propertyList:
        keyVal = prop.split("=")
        propKey = keyVal[0]
        if propKey == propName and not propKey.startswith("#"):
            propVal = keyVal[1].replace("\n", "")
            if multiple:
                rtnProps.append(propVal)
            else:
                return propVal
    if multiple:
        return rtnProps
    else:
        return None

