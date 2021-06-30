import time

def Initialization():
    # Global Parameters:
    global Vehicle_Type_C2X_no_message
    global Vehicle_Type_C2X_HasCurrentMessage
    global d1
    global d2
    global control_to_decel
    global control_to_stop

    Vehicle_Type_C2X_no_message = '630'
    Vehicle_Type_C2X_HasCurrentMessage = '631'
    d1,d2 = Vissim.Net.Detectors.GetAll()
    control_to_decel = 1.5
    control_to_stop = 1

def TTC(Coord_veh, Coord_detector,Speed_veh,Speed_detector):
    PositionXYZ_veh = Coord_veh.split(" ")
    PositionXYZ_det = Coord_detector.split(" ")
    PositionXYZ_veh = list(map(float,PositionXYZ_veh))
    PositionXYZ_det = list(map(float,PositionXYZ_det))

    numerator = ( ( (PositionXYZ_veh[0] - PositionXYZ_det[0])**2 ) + ( (PositionXYZ_veh[1] - PositionXYZ_det[1])**2 ) )**0.5
    denominator = abs(Speed_veh-(-Speed_detector)) # due to direction
    if denominator==0 : denominator=0.0001
    ttc = numerator/denominator

    if ttc<control_to_stop :
        speed_to_desire = 0
        decision_veh = 0

    elif ttc<control_to_decel :
        speed_to_desire1 = (numerator/control_to_decel) + Speed_detector
        speed_to_desire2 = -(numerator/control_to_decel) + Speed_detector
        if speed_to_desire1 < Speed_veh:
            speed_to_desire = speed_to_desire1
            decision_veh = 2
        else :
            if speed_to_desire2 <= 0 :
                speed_to_desire = 0
                decision_veh = 0
            else :
                speed_to_desire = speed_to_desire2
                decision_veh = 2

    else :
        speed_to_desire = None
        decision_veh = 1

    return (ttc, decision_veh, speed_to_desire, numerator)



def D2V():
    Veh_attributes = Vissim.Net.Vehicles.GetMultipleAttributes(('RoutDecType', 'RoutDecNo', 'VehType', 'No'))
    sending_message=[]
    if Veh_attributes:
        # detection
        if d1.AttValue('VehNo') or d2.AttValue('VehNo'):
            if d1.AttValue('VehNo') : sending_message.append((d1.AttValue('VehNo'),round(d1.AttValue('VehSpeed'),4)))
            if d2.AttValue('VehNo') : sending_message.append((d2.AttValue('VehNo'),round(d2.AttValue('VehSpeed'),4)))

        # get C2X Cars
        Veh_C2X_attributes = [item for item in Veh_attributes if item[2] == Vehicle_Type_C2X_no_message or item[2] == Vehicle_Type_C2X_HasCurrentMessage]
        for cnt_C2X_veh in range(len(Veh_C2X_attributes)):
            start = time.time()
            Veh_sending_Msg = Vissim.Net.Vehicles.ItemByKey(Veh_C2X_attributes[cnt_C2X_veh][3])

            # choose cars to left
            if ((Veh_sending_Msg.AttValue('NextLink')=='10004' ) and (Veh_sending_Msg.AttValue('Pos')>210)) or ((Veh_sending_Msg.AttValue('Lane')=='10004-1' ) and (Veh_sending_Msg.AttValue('Pos')<3)):
                    Speed_veh = Veh_sending_Msg.AttValue('Speed')
                    DesSpeed_Veh = Veh_sending_Msg.AttValue('DesSpeed')
                    DesSpeedOld_Veh = Veh_sending_Msg.AttValue('C2X_DesSpeedOld')
                    Coord_Veh    = Veh_sending_Msg.AttValue('CoordFront') 
                    Decision_Veh    = Veh_sending_Msg.AttValue('C2X_Decision') 
                    decision_value = None
                    decision_time = Veh_sending_Msg.AttValue('C2X_Decision_time') 

                    if Veh_sending_Msg.AttValue('C2X_HasCurrentMessage') != 1 : Veh_sending_Msg.SetAttValue('C2X_HasCurrentMessage', 1)
                    if Veh_sending_Msg.AttValue('C2X_SendingMessage') != 1    : Veh_sending_Msg.SetAttValue('C2X_SendingMessage', 1)
                    Veh_sending_Msg.SetAttValue('C2X_Message', f"{sending_message}")

                    if Veh_sending_Msg.AttValue('VehType')=='630':
                        Veh_sending_Msg.SetAttValue('VehType', '631')
                        # print('-'*100)
                        # print("[NEW]",end='\t')
                    else :
                        # print('-'*100)
                        # print("[MOD]",end='\t')
                    # print(f"No. : {Veh_sending_Msg.AttValue('No')}",end='\t')
                    # print(f"Speed : {round(Speed_veh,4)}",end='\t')
                    # print(f"DesSpeed : {round(DesSpeed_Veh,4)}",end='\t')
                    # print(f"MSG : {Veh_sending_Msg.AttValue('C2X_Message')}")
                        pass
                    ### TTC
                    # ttc, decision_veh, speed_to_desire
                    temp = 999999
                    for decision in sending_message:
                        coord_detector = Vissim.Net.Vehicles.ItemByKey(decision[0]).AttValue('CoordFront') 
                        ttc_items = TTC(Coord_Veh, coord_detector,Speed_veh,decision[1])
                        # print(f"\tTTC with object{decision[0]} : {round(ttc_items[0],5)}",end="\t")
                        # print(f"Distance : {round(ttc_items[3],4)}")
                        if temp > ttc_items[0] : 
                            temp = ttc_items[0]
                            decision_value = ttc_items



                        

                    # 속도변경
                    if decision_value: 
                        # 기존에 Stop or Decel 판단을 내리지 않은 경우 or 기존에 Stop or Decel 판단을 내렸던 판단이 만료된 경우
                        if Veh_sending_Msg.AttValue('C2X_Decision_time')==0 or Vissim.Simulation.SimulationSecond > Veh_sending_Msg.AttValue('C2X_Decision_time') : 
                            if decision_value[1]==0:
                                # print("\n\tDecision : [STOP]",end=' ')
                                if DesSpeedOld_Veh :
                                    Veh_sending_Msg.SetAttValue('DesSpeed',decision_value[2])
                                    decision_time = Vissim.Simulation.SimulationSecond + decision_value[0]
                                    Veh_sending_Msg.SetAttValue('C2X_Decision_time',decision_time)
                                else :
                                    Veh_sending_Msg.SetAttValue('C2X_DesSpeedOld',DesSpeed_Veh)
                                    Veh_sending_Msg.SetAttValue('DesSpeed',decision_value[2])
                                    decision_time = Vissim.Simulation.SimulationSecond + decision_value[0]
                                    Veh_sending_Msg.SetAttValue('C2X_Decision_time',decision_time)

                                if Decision_Veh != 0 : 
                                    Veh_sending_Msg.SetAttValue('C2X_Decision',0)
                                # print(f"{Veh_sending_Msg.AttValue('C2X_Decision')}",end='\t')
                                # print(f"Expired : {round(Veh_sending_Msg.AttValue('C2X_Decision_time'),2)}",end='\t')

                            elif decision_value[1]==1:
                                # print("\n\tDecision : [GO]",end=' ')
                                if DesSpeedOld_Veh :
                                    if DesSpeedOld_Veh<5:
                                        Veh_sending_Msg.SetAttValue('DesSpeed',25)
                                    else :
                                        Veh_sending_Msg.SetAttValue('DesSpeed',DesSpeedOld_Veh)
                                else :
                                    pass
                                if Decision_Veh != 1 : 
                                    Veh_sending_Msg.SetAttValue('C2X_Decision',1)
                                # print(f"{Veh_sending_Msg.AttValue('C2X_Decision')}",end='\t')

                            elif decision_value[1]==2:
                                # print("\n\tDecision : [DECEL]",end=' ')
                                if DesSpeedOld_Veh :
                                    if DesSpeed_Veh > decision_value[2]:
                                        Veh_sending_Msg.SetAttValue('DesSpeed',decision_value[2])
                                        decision_time = Vissim.Simulation.SimulationSecond + decision_value[0]
                                        Veh_sending_Msg.SetAttValue('C2X_Decision_time',decision_time)
                                    else :
                                        pass
                                else :
                                    Veh_sending_Msg.SetAttValue('C2X_DesSpeedOld',DesSpeed_Veh)
                                    Veh_sending_Msg.SetAttValue('DesSpeed',decision_value[2])
                                    decision_time = Vissim.Simulation.SimulationSecond + decision_value[0]
                                    Veh_sending_Msg.SetAttValue('C2X_Decision_time',decision_time)
                                if Decision_Veh != 2 : 
                                    Veh_sending_Msg.SetAttValue('C2X_Decision',2)
                                # print(f"{Veh_sending_Msg.AttValue('C2X_Decision')}",end='\t')
                                # print(f"Expired : {round(Veh_sending_Msg.AttValue('C2X_Decision_time'),2)}",end='\t')

                        # 기존에 Stop or Decel 판단을 내렸던 판단이 만료되지 않은 경우 :
                        elif Vissim.Simulation.SimulationSecond < Veh_sending_Msg.AttValue('C2X_Decision_time') :
                            decision_time = Vissim.Simulation.SimulationSecond + decision_value[0]

                            if decision_value[1]==0:
                                # print("\n\tDecision : [STOP]",end=' ')
                                if DesSpeedOld_Veh :
                                    Veh_sending_Msg.SetAttValue('DesSpeed',decision_value[2])
                                    decision_time = Vissim.Simulation.SimulationSecond + decision_value[0]
                                    Veh_sending_Msg.SetAttValue('C2X_Decision_time',decision_time)
                                else :
                                    Veh_sending_Msg.SetAttValue('C2X_DesSpeedOld',DesSpeed_Veh)
                                    Veh_sending_Msg.SetAttValue('DesSpeed',decision_value[2])
                                    decision_time = Vissim.Simulation.SimulationSecond + decision_value[0]
                                    Veh_sending_Msg.SetAttValue('C2X_Decision_time',decision_time)
                                if Decision_Veh != 0 : 
                                    Veh_sending_Msg.SetAttValue('C2X_Decision',0)
                                # print(f"{Veh_sending_Msg.AttValue('C2X_Decision')}",end='\t')
                                # print(f"Expired : {round(Veh_sending_Msg.AttValue('C2X_Decision_time'),2)}",end='\t')

                            elif decision_value[1]==1:
                                # 만료되지 않았으므로 0 or 2 유지
                                if Veh_sending_Msg.AttValue('C2X_Decision')==0:
                                    # print("\n\tDecision : [STOP]",end=' ')
                                    # print(f"{Veh_sending_Msg.AttValue('C2X_Decision')}",end='\t')
                                    # print(f"Expired : {round(Veh_sending_Msg.AttValue('C2X_Decision_time'),2)}",end='\t')
                                    pass
                                elif Veh_sending_Msg.AttValue('C2X_Decision')==1:
                                    # print("********ERROR : 만료되지 않은 명령**********")
                                    pass
                                elif Veh_sending_Msg.AttValue('C2X_Decision')==2:
                                    # print("\n\tDecision : [DECEL]",end=' ')
                                    # print(f"{Veh_sending_Msg.AttValue('C2X_Decision')}",end='\t')
                                    # print(f"Expired : {round(Veh_sending_Msg.AttValue('C2X_Decision_time'),2)}",end='\t')
                                    pass
                            elif decision_value[1]==2:
                                if Veh_sending_Msg.AttValue('C2X_Decision')==0:
                                    # print("\n\tDecision : [STOP]",end=' ')
                                    # print(f"{Veh_sending_Msg.AttValue('C2X_Decision')}",end='\t')
                                    # print(f"Expired : {round(Veh_sending_Msg.AttValue('C2X_Decision_time'),2)}",end='\t')
                                    pass
                                elif Veh_sending_Msg.AttValue('C2X_Decision')==1:
                                # if Veh_sending_Msg.AttValue('C2X_Decision')==1:
                                    # print("\n\tDecision : [GO]",end=' ')
                                    if DesSpeedOld_Veh :
                                        if DesSpeed_Veh < 5 :
                                            Veh_sending_Msg.SetAttValue('DesSpeed',DesSpeedOld_Veh)
                                    else :
                                        pass
                                    if Decision_Veh != 1 : 
                                        Veh_sending_Msg.SetAttValue('C2X_Decision',1)
                                    # print(f"{Veh_sending_Msg.AttValue('C2X_Decision')}",end='\t')

                                elif Veh_sending_Msg.AttValue('C2X_Decision')==2:
                                    # print("\n\tDecision : [DECEL]",end=' ')
                                    if DesSpeedOld_Veh :
                                        if DesSpeed_Veh > decision_value[2]:
                                            Veh_sending_Msg.SetAttValue('DesSpeed',decision_value[2])
                                            decision_time = Vissim.Simulation.SimulationSecond + decision_value[0]
                                            Veh_sending_Msg.SetAttValue('C2X_Decision_time',decision_time)
                                        else :
                                            pass
                                    else :
                                        Veh_sending_Msg.SetAttValue('C2X_DesSpeedOld',DesSpeed_Veh)
                                        Veh_sending_Msg.SetAttValue('DesSpeed',decision_value[2])
                                        decision_time = Vissim.Simulation.SimulationSecond + decision_value[0]
                                        Veh_sending_Msg.SetAttValue('C2X_Decision_time',decision_time)
                                    if Decision_Veh != 2 : 
                                        Veh_sending_Msg.SetAttValue('C2X_Decision',2)
                                    # print(f"{Veh_sending_Msg.AttValue('C2X_Decision')}",end='\t')
                                    # print(f"Expired : {round(Veh_sending_Msg.AttValue('C2X_Decision_time'),2)}",end='\t') 

                        # print(f"\tDesSpeed : {round(Veh_sending_Msg.AttValue('DesSpeed'),5)}",end="\t")
                        if decision_value : 
                            if decision_value[1]!=1 : 
                                # print(f"TTC Speed : {round(decision_value[2],4)}",end='\t')
                                pass
                        # print(f"time elapsed  : {round(time.time()-start,5)}")

                    # 만료되었고, vehicle이 없는 상태에서의 판단
                    elif Vissim.Simulation.SimulationSecond > Veh_sending_Msg.AttValue('C2X_Decision_time') :
                        # print("\n\tDecision : [GO]",end=' ')
                        if DesSpeedOld_Veh<5:
                            Veh_sending_Msg.SetAttValue('DesSpeed',25)
                        else :
                            Veh_sending_Msg.SetAttValue('DesSpeed',DesSpeedOld_Veh)
                            
                        if Decision_Veh != 1 : 
                            Veh_sending_Msg.SetAttValue('C2X_Decision',1)
                        # print(f"{Veh_sending_Msg.AttValue('C2X_Decision')}",end='\t')
                        # print(f"\tDesSpeed : {round(Veh_sending_Msg.AttValue('DesSpeed'),5)}",end="\t")
                        # print(f"time elapsed  : {round(time.time()-start,5)}")

            # 메세지를 수신한 상태에서, 5-2에서 벗어난 차량이라면
            elif (Veh_sending_Msg.AttValue('C2X_HasCurrentMessage')==1) and ((Veh_sending_Msg.AttValue('Lane')!='5-2') and ((Veh_sending_Msg.AttValue('Lane')!='10004') and (Veh_sending_Msg.AttValue('POS')>3))):
                DesSpeedOld_Veh = Veh_sending_Msg.AttValue('C2X_DesSpeedOld')
                DesSpeed_Veh = Veh_sending_Msg.AttValue('DesSpeed')
                Veh_sending_Msg.SetAttValue('C2X_HasCurrentMessage', 0)
                Veh_sending_Msg.SetAttValue('C2X_SendingMessage', 0)
                Veh_sending_Msg.SetAttValue('C2X_Message', '')
                Veh_sending_Msg.SetAttValue('VehType', '630')
                if DesSpeedOld_Veh : Veh_sending_Msg.SetAttValue('DesSpeed',DesSpeedOld_Veh)
                # print('-'*100)
                # print(f"Veh[{Veh_sending_Msg.AttValue('No')}] Passed", end='\t')
                # print(f"Speed_to_desire : {round(DesSpeed_Veh,4)}",end='\t')
                # print(f"time elapsed  : {round(time.time()-start,5)}")
            else :
                pass

def RunMultipleStep(iter):
    for _ in range(iter):
        Vissim.Simulation.RunSingleStep()


if __name__=="__main__":
        
    import win32com.client as com

    ### 24
    Vissim = com.gencache.EnsureDispatch("Vissim.Vissim")
    NetPath=r"C:\Users\user\Desktop\LeftTurn\left turn real.inpx"
    Vissim.LoadNet(NetPath)
    Initialization()
    while True:
        inp = input("how many step?")
        try :
            if inp != 'break':
                for i in range(int(inp)) : 
                    RunMultipleStep(3)
                    D2V()
            elif inp == 'break':
                break
        except :
            print("숫자 또는 'break'를 입력해주세요.")
            continue
    Vissim = None

    # ### 25
    # Vissim = com.gencache.EnsureDispatch("Vissim.Vissim")
    # NetPath=r"C:\Users\user\Desktop\LeftTurn\left turn real.inpx"
    # Vissim.LoadNet(NetPath)
    # Initialization()
    # for i in range(1000) : 
    #     RunMultipleStep(3)
    #     # D2V()
    # Vissim = None
