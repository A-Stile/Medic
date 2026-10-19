diseases = {"flu": .3, "supbro": .7}

def response_builder(diseases):
    message = ""
    if sum(diseases.values()) > 1:
        return "Values have a greater sum than 1"
    for i, j in diseases.items():
        if j >= .9:
            message += f"There is a highly likely chance you have {i}. "
        if .9 > j >= .8:
            message += f"You most likey have {i}. "
        if .8 > j >= .7:
            message += f"There is a stong chance you have {i}. "
        if .7 > j >= .6:
            message += f"You likely have {i}. "
        if .6 > j >= .5:
            message += f"It is probable that you have {i}. "
        if .5 > j >= .4:
            message += f"There is a chance you have {i}. "
        if .4 > j >= .3:
            message += f"There is a possibility that you have {i}. "
        if .3 > j >= .2:
            message += f"There is a small possibility that you have {i}. "
        if .2 > j >= .1:
            message += f"There is a very little chance you have {i}. "
        if .1 > j:
            message += f"There is a highly unlikely chance you have {i}. "
        message += "\n"
    return message
            
print(response_builder(diseases), end = "")

