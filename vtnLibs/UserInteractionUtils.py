from vtnLibs.common_utils.LogUtils import LogEnabledClass as lec

class UserInputUtils(lec):
    QUIT_LOOP="quid"
    VALID_INPUT="ok"
    INVALID_INPUT="KO"
    # INVALID_INPUT="loop"
    @staticmethod
    def getUserInput(message, displayMenuCallback, userInputControlCallback, refreshManu=False):
        loop=True
        while loop:
            displayMenuCallback()
            userInput = input(message)
            UserInputUtils.debug(f"user has keyed:{userInput}")
            controlResult = userInputControlCallback(userInput=userInput)
            if(controlResult==UserInputUtils.QUIT_LOOP or controlResult==UserInputUtils.VALID_INPUT ):
                loop=False

    @staticmethod
    def defaultUserCOntrolCallback( userInput):
        if (userInput.strip().lower()=="q"):
            UserInputUtils.debug(f"user wants to quit ")
            return UserInputUtils.QUIT_LOOP
        UserInputUtils.debug(f" ANy other action than quit is valid")
        return UserInputUtils.VALID_INPUT

