# python linux_gpio_fonksiyon.py  101
# python linux_gpio_fonksiyon.py  103

# nanopi_neo3  için ################################################################################################

#    All pins are 3.3V, output current is 5mA
    
#    Pin#    Name                    Linux GPIO    Pin#    Name            Linux GPIO
#    1        3.3V(OUT)                             2    5V(OUT/IN)    
#    3        I2C0_SDA                              4    5V(OUT/IN)    
#    5        I2C0_SCL                              6    GND    
#    7        GPIO2_A2/IR-RX             66         8    GPIO3_A4/UART1_TX    100
#    9        GND                                  10    GPIO3_A6/UART1_RX    102
#    11       GPIO2_B7/I2S1_MCLK         79        12    GPIO2_C3/I2S1_SDI     83
#    13       GPIO2_C1/I2S1_LRCK_TX      81        14    GND    
#    15       GPIO2_C2/I2S1_SCLK         82        16    GPIO3_A5/UART1_RTSN  101       -->>>
#    17       3.3V(OUT)                            18    GPIO3_A7/UART1_CTSN  103       -->>>
#    19       GPIO3_A1/SPI_TXD           97        20    GND    
#    21       GPIO3_A2/SPI_RXD           98        22    GPIO2_C7/I2S1_SDO     87
#    23       GPIO3_A0/SPI_CLK           96        24    GPIO3_B0/SPI_CSN0    104
#    25       GND                                  26    GPIO0_D3/SPDIF_TX     27
#    FAN      GPIO2_A6/PWM2              70        AO3415A mosfet ile 4A (5V) fan kontrolü yapabiliyor

# --------------------
# echo 66 > /sys/class/gpio/export
# echo $?        ilk exportta 0 döner

# echo 66 > /sys/class/gpio/unexport

# echo out > /sys/class/gpio/gpio66/direction
# echo $?        0 döner

# echo 1  > /sys/class/gpio/gpio66/value

# echo in > /sys/class/gpio/gpio66/direction
# echo 1 > /sys/class/gpio/gpio66/active_low   #  input girişine tersleyici takar
# cat /sys/class/gpio/gpio66/value

# GPIO2_A6/PWM2  aktif etmek için:  ---------------------------------------------
    # /boot/dtb-5.15.84-rockchip64/rockchip/overlay/rockchip-pwm-gpio.dts   içine aşağıdakini kaydet:
####
# /dts-v1/;
# /plugin/;

# / {
        # compatible = "rockchip,rk3328";
        
        # fragment@0 {
                # target-path = "/pwm@ff1b0020";
                # __overlay__ {
                        # status = "okay";
                # };
        # };

# };
####
    # /etc/udev/rules.d/50-pwm.rules içine aşağıdakini kaydet:
####
# SUBSYSTEM=="pwm*", PROGRAM="/bin/sh -c '\
        # chown -R root:gpio /sys/class/pwm && chmod -R 770 /sys/class/pwm;\
        # chown -R root:gpio /sys/devices/platform/*.pwm/pwm/pwmchip* && chmod -R 770 /sys/devices/platform/*.pwm/pwm/pwmchip*\
# '"
####
    # cd /boot/dtb-5.15.84-rockchip64/rockchip/overlay
    # dtc -I dts -O dtb rockchip-pwm-gpio.dts -o rockchip-pwm-gpio.dtbo
    # sudo shutdown -r now     # -h kapatır  -r yeniden başlatır
    # udevadm control --reload-rules ; udevadm trigger
    # cat  /sys/kernel/debug/pwm
    
    # echo 0 > /sys/class/pwm/pwmchip0/export
    # echo 10000000 > /sys/class/pwm/pwmchip0/pwm0/period     #set period to 10ms
    # echo "inversed" > /sys/class/pwm/pwmchip0/pwm0/polarity
    # echo "normal" > /sys/class/pwm/pwmchip0/pwm0/polarity
    # echo 1 > /sys/class/pwm/pwmchip0/pwm0/enable
    # echo 5000000 > /sys/class/pwm/pwmchip0/pwm0/duty_cycle  # set duty cycle to 5ms
# ---------------------------------------------------------------------------------

################################################################################################
import time,os,sys
import subprocess

kizilotesi_Linux_GPIO_pin=101 #linux gpio numarası
kirmizi_Linux_GPIO_pin=103
deneme_giris_pin=66

def gpioDurum():
    donusKodInt,ciktiTum,ciktiStd,ciktiErr=komut_calistir('cat /sys/kernel/debug/gpio')
    return '\n-------------------\ncat  /sys/kernel/debug/gpio\n\n:' + ciktiTum + '\n ------------------- \n'


def pinMode(pin, io_mod):  
    donusKodInt,ciktiTum,ciktiStd,ciktiErr=komut_calistir('echo ' + str(pin) + ' > /sys/class/gpio/export')
    if ( donusKodInt!=0 and donusKodInt!=1 ):
        return 'Başarısız   pinMode('+str(pin)+',\'' + io_mod + '\') : echo ' + str(pin) + ' > /sys/class/gpio/export ' + '            ciktiErr=' + ciktiErr +  '  donusKodInt=' + str(donusKodInt)
    donusKodInt,ciktiTum,ciktiStd,ciktiErr=komut_calistir('echo ' + io_mod + ' > /sys/class/gpio/gpio' + str(pin) + '/direction')
    if donusKodInt!=0:
        return 'Başarısız   pinMode('+str(pin)+',\'' + io_mod + '\') :  echo ' + io_mod + ' > /sys/class/gpio/gpio' + str(pin) + '/direction' +  '            ciktiErr=' + ciktiErr +  '  donusKodInt=' + str(donusKodInt)
    return 'Basarili'

def digitalWrite(pin,io_deger,python_ile_oku_yaz=False):
    global python_ile_oku_yaz_
    python_ile_oku_yaz_=python_ile_oku_yaz
    donusKodInt,ciktiTum,ciktiStd,ciktiErr=komut_calistir('echo ' + str(io_deger) + ' > /sys/class/gpio/gpio' + str(pin) + '/value',python_ile_oku_yaz_)

    if donusKodInt!=0:
        return 'Başarısız   digitalWrite('+str(pin)+',\'' + str(io_deger) + '\') :  echo ' + str(io_deger) + ' > /sys/class/gpio/gpio' + str(pin) + '/value' +  '            ciktiErr=' + ciktiErr +  '  donusKodInt=' + str(donusKodInt)

    return 'Basarili'

def digitalRead(pin,python_ile_oku_yaz=False,sonucu_int_olarak_dondur=True):
    global python_ile_oku_yaz_
    python_ile_oku_yaz_=python_ile_oku_yaz
    donusKodInt,ciktiTum,ciktiStd,ciktiErr=komut_calistir('cat ' + '/sys/class/gpio/gpio' + str(pin) + '/value',python_ile_oku_yaz_)

    if donusKodInt!=0:
        if sonucu_int_olarak_dondur:
            return -1
        return 'Başarısız  digitalRead('+str(pin)+') :  cat ' + '/sys/class/gpio/gpio' + str(pin) + '/value' +  '            ciktiErr=' + ciktiErr +  '  donusKodInt=' + str(donusKodInt) 
    if sonucu_int_olarak_dondur:
        return int(ciktiStd)
    return ciktiStd

################################################################################################
###################################################################################################################

import time
import threading

def thread_1_baslat():
    global thread_1_tetik,thread_1,thread_1_komutReturnCode,thread_1_tetik_2
    thread_1_tetik = threading.Event();thread_1_tetik_2 = threading.Event()
    thread_1 = threading.Thread(name='tetiklenebilir_thread',  target=thread_1_is_fonksiyonu, args=(thread_1_tetik,))
    thread_1.daemon = True
    thread_1.start()
    return '\tTHREAD - %s - PID: %s ' % (thread_1.getName(),str(thread_1.native_id))

def thread_1_gorev_ver(yeni_komut,python_ile_oku_yaz=False):
    global thread_1_yeni_komut,thread_1_komutReturnCode,python_ile_oku_yaz_
    python_ile_oku_yaz_=python_ile_oku_yaz
    thread_1_yeni_komut=yeni_komut
    thread_1_komutReturnCode=None;
    thread_1_tetik.set()


def thread_1_is_fonksiyonu(thread_1_tetik):
    global thread_1,thread_1_yeni_komut,python_ile_oku_yaz_                     ,thread_1_komutReturnCode,komutReturnCode,komutCiktiStd,komutCiktiErr,komutCikti,komutCiktiOnceki,lojik
    while True:
        tetik_aktif_mi = thread_1_tetik.wait()

        komut_calistir(thread_1_yeni_komut,python_ile_oku_yaz_)
        thread_1_tetik_2.set()
        thread_1_tetik.clear()


def komut_calistir_degiskenleri_baslat():
    global thread_1_komutReturnCode,islem,komut,komutReturnCode,komutCikti,komutCiktiStd,komutCiktiErr,komutOnceki,komutReturnCodeOnceki,komutCiktiOnceki,komutCiktiStdOnceki,komutCiktiErrOnceki
    islem=None;komut="";komutReturnCode=None;komutCikti="";komutCiktiStd="";komutCiktiErr="";komutOnceki="";komutReturnCodeOnceki=None;komutCiktiOnceki="";komutCiktiStdOnceki="";komutCiktiErrOnceki=""
    
def komut_calistir(yeni_komut,python_ile_oku_yaz=False):
# islem="";komut="";komutReturnCode=None;komutCikti="";komutCiktiStd="";komutCiktiErr="";komutOnceki="";komutReturnCodeOnceki=None;komutCiktiOnceki="";komutCiktiStdOnceki="";komutCiktiErrOnceki=""
    global thread_1_komutReturnCode,islem,komut,komutReturnCode,komutCikti,komutCiktiStd,komutCiktiErr,komutOnceki,komutReturnCodeOnceki,komutCiktiOnceki,komutCiktiStdOnceki,komutCiktiErrOnceki
    # print(yeni_komut)
    komutOnceki=komut;komutReturnCodeOnceki=komutReturnCode;komutCiktiOnceki=komutCikti;komutCiktiStdOnceki=komutCiktiStd;komutCiktiErrOnceki=komutCiktiErr
    komut=yeni_komut;komutReturnCode=None;komutCikti="";komutCiktiStd="";komutCiktiErr=""
        # print( 'son   komutReturnCode='  + str(komutReturnCode) +'=     komutCikti=' + str(komutCikti) + '=    komutCiktiStd=' + str(komutCiktiStd) + '=     ???????????komutCiktiErr=' + str(komutCiktiErr) +  '=' )

    if python_ile_oku_yaz:              # fiziksel olarak çıkış pininden giriş pinine tel bağlayıp; verilen çıkışın girişten alınma gecikmesi en fazla  798 mikro saniye olmakta (with open kullanıldığı için bu kadar hızlı)
        komut_args=komut.split()
        if komut_args[0]=='cat':
            # print('oku')
            komut_args_yol=komut_args[1]
            with open(komut_args_yol,'r') as f:       # ekrana basılmazsa  saniyede en fazla    2161 okuma  yapılabiliyor (işlemci ortalama kullanımı %29)
                komutCikti = f.read().strip()         # okuma python_ile_oku_yaz=True 2111   python_ile_oku_yaz=False  171    (işlemci ortalama kullanımı %30)
                komutCiktiStd=komutCikti
            komutCiktiErr=""
            komutReturnCode=0
            # print( 'okunan_deger=' + komutCikti)
        elif komut_args[0]=='echo':
            # print('yaz')
            komut_args_deger=komut_args[1]
            # print( 'komut_args_deger=' + komut_args_deger)
            komut_args_yol=komut_args[3]
            with open(komut_args_yol, 'w') as file2:  # ekrana basılmazsa  saniyede en fazla    2217 yazma  yapılabiliyor (işlemci ortalama kullanımı %30)
                file2.write(komut_args_deger)         # yazma python_ile_oku_yaz=True 2200   python_ile_oku_yaz=False  304     (işlemci ortalama kullanımı %29)
            komutCiktiStd=""
            komutCiktiErr=""
            komutReturnCode=0
        else:
            komutReturnCode=-1
            komutCikti=""
            komutCiktiStd=""
            komutCiktiErr=" python_ile_oku_yaz=True  parametresini kullanmışsın ama komutun   cat   veya   echo  ile başlamamış! "
            return (komutReturnCode,komutCikti,komutCiktiStd,komutCiktiErr)

    else:
        islem = subprocess.Popen(komut,  shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,text=True) # ekrana basılmadığı durumda --># komut,  shell=True --> saniyede 183 okuma (işlemci ortalama kullanımı %29)  , 305 yazma (işlemci ortalama kullanımı %32); komut.split(),  shell=False --> saniyede 250 okuma (Fakat bunda yazma komutu çalışmıyor)
        # komutCiktiStd,komutCiktiErr= islem.communicate()

        for line in iter(islem.stdout.readline, ""):
            # print ('=' + str(line.strip()) + '=')
            komutCiktiStd += str(line)
            komutCikti += str(line)

            # time.sleep(0.1)

        for line in iter(islem.stderr.readline, ""):
            # print ('=' + str(line.strip()) + '=')
            komutCiktiErr += str(line)
            komutCikti += str(line)
            
            # time.sleep(0.1)
        islem.wait()
        
        komutCikti=komutCikti.strip()
        komutCiktiStd=komutCiktiStd.strip()
        komutCiktiErr=komutCiktiErr.strip()
        komutReturnCode = islem.returncode
        thread_1_komutReturnCode = komutReturnCode

    return (komutReturnCode,komutCikti,komutCiktiStd,komutCiktiErr)
    

#########################################################################


if __name__ == '__main__':
    komut_calistir_degiskenleri_baslat()
    print(thread_1_baslat());#time.sleep(6)
    print(' ========= os.getpid()=' + str(os.getpid())) 

    try:
        arg1 = sys.argv[1]
        arg2 = sys.argv[2]
        arg3 = sys.argv[3]
        arg4 = sys.argv[4]
        arg5 = sys.argv[5]
    except:
        pass


    print( 'kizilotesi_Linux_GPIO_pin=' + str(kizilotesi_Linux_GPIO_pin) + '    kirmizi_Linux_GPIO_pin=' + str(kirmizi_Linux_GPIO_pin) )

    print(gpioDurum())
    # arg1_pin_no=int(arg1)

################################ giriş veya çıkış olarak ayar

    # basariDurumu=pinMode(arg1_pin_no, 'out' )  # pinMode(integer_Linux_GPIO_pin_numarası, 'out' )   veya   pinMode(integer_Linux_GPIO_pin_numarası, 'in' )
    
    basariDurumu=pinMode(kirmizi_Linux_GPIO_pin, 'out' )  
    if( basariDurumu!='Basarili' ):
        print(basariDurumu);

    basariDurumu=pinMode(kizilotesi_Linux_GPIO_pin, 'out' )  
    if( basariDurumu!='Basarili' ):
        print(basariDurumu);


    # basariDurumu=pinMode(deneme_giris_pin, 'in' )
    # if( basariDurumu!='Basarili' ):
        # print(basariDurumu);

################################ pin yazma

    lojik='0'
    while True:
    
        thread_1_gorev_ver('echo ' + lojik + ' >  /sys/class/gpio/gpio' + str(kizilotesi_Linux_GPIO_pin) + '/value',python_ile_oku_yaz=True)  # yazma python_ile_oku_yaz=True ise saniyede en fazla 2200 kez (bu değeri elde etmek için; sonsuz döngüde ekrana yazı bastırma kapatılmalı ) ;   python_ile_oku_yaz=False ise saniyede en fazla   304       (işlemci ortalama kullanımı %29)
        thread_1_tetik_2.wait();thread_1_tetik_2.clear()

        if lojik=='1':
            lojik='0' ;
        else:
            lojik='1' ;

        thread_1_gorev_ver('echo ' + lojik + ' >  /sys/class/gpio/gpio' + str(kirmizi_Linux_GPIO_pin) + '/value',python_ile_oku_yaz=True)  # yazma python_ile_oku_yaz=True ise saniyede en fazla 2200 kez (bu değeri elde etmek için; sonsuz döngüde ekrana yazı bastırma kapatılmalı ) ;   python_ile_oku_yaz=False ise saniyede en fazla   304       (işlemci ortalama kullanımı %29)
        thread_1_tetik_2.wait();thread_1_tetik_2.clear()

        # time.sleep(1)

        # time.sleep(0.033) # saniyede 30 frame
        # time.sleep(0.025) # saniyede 40 frame
        # time.sleep(0.016) # saniyede 60 frame
        time.sleep(0.010) # saniyede 100 frame



################################ pin okuma

    # komutCiktiOnceki='0'
    
    deger=0
    while True:
    
        thread_1_gorev_ver('cat /sys/class/gpio/gpio' + str(deneme_giris_pin) + '/value',python_ile_oku_yaz=True)                       # okuma python_ile_oku_yaz=True  ise saniyede en fazla   2111 kez (bu değeri elde etmek için; sonsuz döngüde ekrana yazı bastırma kapatılmalı ) ;   python_ile_oku_yaz=False ise saniyede en fazla     171 kez       (işlemci ortalama kullanımı %30)

        thread_1_tetik_2.wait();thread_1_tetik_2.clear()
        
        # time.sleep(0.005)


        # if True:
        if True:  #  Bunun yerine saniyede bir kere ekrana bastırılırsa  yüksek hızlara(saniyede 2100) çıkılabilir

            
            try:
                deger=int(komutCikti)
            except:
                deger=int(komutCiktiOnceki)
            
            print('    pin deneme_giris_pin='+ str(deneme_giris_pin) + ' okunan deger:' + str(deger)  ,end='')
            if deger==0:
                print('  ========================' )
            elif deger==1:
                print('' )


        time.sleep(1)
