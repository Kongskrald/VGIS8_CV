MODULE InitParameters
        
PROC IP_Initialize()
    ConfL\Off;
    ConfJ\Off;
    
    ! Mapping default tool and work object that you want to work with
    !defaultTool := tool0;
    !defaultWobj := wobj0;   
    
    ! Mapping signals related to controlling a gripper
    !AliasIO Gripper_On_Off0, defaultGripperActivationIO;
    !AliasIO Gripper_On_Off_Executed0, defaultGripperActionExecutedIO;
    !AliasIO Gripper_Grasp_State0, defaultGripperObjectStateIO;
    
    ! Mapping signals related to controlling a camera 
    !AliasIO Take_Picture0, defaultTakePictureActivationIO;
    !AliasIO Take_Picture_Executed0, defaultTakePictureExecutedIO;
    
ENDPROC
    
ENDMODULE