from pydbg import *
from pydbg.defines import *
import ctypes
import struct
from broker_calls import *
import psutil


# shdocvwBroker object interface
shdocvw_offset = 0x12bd8
shdocvw_entry  = 121
shdocvw_names = get_shdocvw_calls_name()


# IERecoveryStore object interface
ierecovery_store_offset = 0xf4db0
ierecovery_store_entry = 36
ierecovery_store_names = get_ierecovery_store_calls_name()


# SettingsStore object interface
settingsstore_offset = 0x187c0c
settingsstore_entry = 9
settingsstore_names = get_settingsstore_calls_name()


# IEUserBroker object interface
ieuser_offset = 0x10ec78
ieuser_entry = 10
ieuser_names = get_ieuser_calls_name()


# stdidentity_unk object interface
stdidentity_unk_offset = 0x34810
stdidentity_unk_entry = 4
stdidentity_unk_names = get_stdidentity_unk_calls_name()


# ieaxinstall object interface
ieaxinstall_offset = 0x114450
ieaxinstall_entry = 4
ieaxinstall_names = get_ieaxinstall_calls_name()


# iereghelperbroker object interface
iereghelperbroker_offset = 0x11441c
iereghelperbroker_entry = 9
iereghelperbroker_names = get_iereghelperbroker_calls_name()


# iereghelperobject_cleanup object interface
iereghelperobject_cleanup_offset = 0x114440
iereghelperobject_cleanup_entry = 4
iereghelperobject_cleanup_names = get_iereghelperobject_cleanup_calls_name()


# iebrokerattach object interface
iebrokerattach_offset = 0x114460
iebrokerattach_entry = 4
iebrokerattach_names = get_iebrokerattach_calls_name()

# protectedmodeAPI object interface
protectedmodeAPI_offset = 0xe3d8
protectedmodeAPI_entry = 8
protectedmodeAPI_names = get_protectedmodeAPI_calls_name()

# feedsloribroker object interface
feedsloribroker_offset = 0x30814
feedsloribroker_entry = 11
feedsloribroker_names = get_feedsloribroker_calls_name()

# feedsarbiterloribroker object interface
feedsarbiterloribroker_offset = 0x4110
feedsarbiterloribroker_entry = 5
feedsarbiterloribroker_names = get_feedsarbiterloribroker_calls_name()

# shellwindow object interface
shellwindow_offset = 0x190020
shellwindow_entry = 18
shellwindow_names = get_shellwindow_calls_name()


# Global variables for dll base address and dictionary function names
broker_global_names_hash = {}
ieframe_image_addr = 0
iertutil_image_addr = 0
ole32_image_addr = 0
msfeeds_image_addr = 0
broker_pid = 0



# Define the breakpoint handler
def handler_breakpoint(pydbg):
    # ignore the first windows driven breakpoint.
    if pydbg.first_breakpoint:
        return DBG_CONTINUE
    
    print "%s called from thread %d" % (broker_global_names_hash[pydbg.exception_address], pydbg.dbg.dwThreadId)
    return DBG_CONTINUE


def install_hooks(pydbg, image_addr, calls_name, offset, calls_n):
    # set a breakpoint in each entry of the interface and update the name dictionary
    for i in range(0, calls_n):
        # Ignore addref, queryInterface and release
        if i < 3:
            continue
        entry = pydbg.read_process_memory(image_addr + offset + 4 * i, 4)
        entry = struct.unpack("<L", entry)[0]
        broker_global_names_hash.update({entry : calls_name[i]})
        pydbg.bp_set(entry)


dbg = pydbg()
    
# register a breakpoint handler function.]
dbg.set_callback(EXCEPTION_BREAKPOINT, handler_breakpoint)

# find the broker process
for i in psutil.process_iter():
    try:
        if i.name == "iexplore.exe":
            if i.parent.name != "iexplore.exe":
                broker_pid = i.pid
    except:
        continue
try:
    dbg.attach(broker_pid)
except:
    print "Unable to attach.... aborting!"
    exit

# find the base address for ieframe.dll and iertutil.dll libraries
for n, addr in dbg.enumerate_modules():
    if n == "IEFRAME.dll":
        ieframe_image_addr = addr
    
    if n == "iertutil.dll":
        iertutil_image_addr = addr

    if n == "ole32.dll":
        ole32_image_addr = addr

    if n == "msfeeds.dll":
        msfeeds_image_addr = addr


# Install hooks
install_hooks(dbg, ieframe_image_addr, iereghelperobject_cleanup_names, iereghelperobject_cleanup_offset, iereghelperobject_cleanup_entry)
install_hooks(dbg, ieframe_image_addr, iereghelperbroker_names, iereghelperbroker_offset, iereghelperbroker_entry)
install_hooks(dbg, ieframe_image_addr, protectedmodeAPI_names, protectedmodeAPI_offset, protectedmodeAPI_entry)
install_hooks(dbg, ieframe_image_addr, shdocvw_names, shdocvw_offset, shdocvw_entry)
install_hooks(dbg, ieframe_image_addr, ierecovery_store_names, ierecovery_store_offset, ierecovery_store_entry)
install_hooks(dbg, ieframe_image_addr, ieuser_names, ieuser_offset, ieuser_entry)
install_hooks(dbg, ole32_image_addr, stdidentity_unk_names, stdidentity_unk_offset, stdidentity_unk_entry)
install_hooks(dbg, ieframe_image_addr, ieaxinstall_names, ieaxinstall_offset, ieaxinstall_entry)
install_hooks(dbg, ieframe_image_addr, iebrokerattach_names, iebrokerattach_offset, iebrokerattach_entry)
install_hooks(dbg, iertutil_image_addr, settingsstore_names, settingsstore_offset, settingsstore_entry)
install_hooks(dbg, msfeeds_image_addr, feedsloribroker_names, feedsloribroker_offset, feedsloribroker_entry)
install_hooks(dbg, msfeeds_image_addr, feedsarbiterloribroker_names, feedsarbiterloribroker_offset, feedsarbiterloribroker_entry)
install_hooks(dbg, iertutil_image_addr, shellwindow_names, shellwindow_offset, shellwindow_entry)

# Start the debug event handler
dbg.debug_event_loop()
