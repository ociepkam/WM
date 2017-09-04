import time


def send_trigger_eeg(trigger_no, port_eeg=None):
    if port_eeg is not None:
        try:
            port_eeg.setData(trigger_no)
            time.sleep(0.01)
            port_eeg.setData(0x00)
        except:
            pass
    trigger_no += 1
    if trigger_no > 21:
        trigger_no = 2
    return trigger_no
