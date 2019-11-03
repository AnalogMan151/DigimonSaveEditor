#!/usr/bin/env python3
# Author: AnalogMan
# Modified Date: 2019-11-03
# Purpose: Applies various edits to a Digimon Story Cyber Sleuth Complete Edition for Nintento Switch save file
# Usage: DigmonSaveEditor.py

from sys import version_info, argv
if version_info <= (3,2,0):
    print('\nPython version 3.2.0+ needed to run this script.')
    exit(1)

from os import remove
from shutil import copy2

CS_Inv_Addr = 0x3EB30
HM_Inv_Addr = 0xA02D0
USABLE_ITEM = 0; EQUIP_ITEM = 1; FARM_ITEM = 2; KEY_TEM = 3; MEDAL_ITEM = 4; ACCESSORY_ITEM = 5

CS_DigiConvert_Addr = 0xB010
HM_DigiConvert_Addr = 0x6C7B0

CS_Money_Addr = 0x4B9B8
HM_Money_Addr = 0xAD158

CS_Party_Mem_Addr = 0x4B9C4
HM_Party_Mem_Addr = 0xAD164

CS_Rank_Addr = 0x4B9C0
HM_Rank_Addr = 0xAD160

CS_Points_Addr = 0x4B9BC
HM_Points_Addr = 0xAD15C

def addToInventory(filepath, inv_addr, item_list, item_type, item_qty):
    try:
        # Open file
        with open(filepath, 'rb+') as f:
            f.seek(inv_addr)
            item_slot = 0
            # Make sure to not go beyond inventory end
            while item_slot < 2000:
                occupied = f.read(4)
                # Check if slot is occupied by an item already. If so, move on to next slot
                if int.from_bytes(occupied, 'little') & 1 == 1:
                    f.seek(20,1)
                    item_slot += 1
                    continue
                f.seek(-4,1)
                break
            index = 0
            while index < len(item_list) and item_slot < 2000:
                occupied = f.read(4)
                # Recheck for empty slot in case empty slots aren't continuous (shouldn't happen)
                if int.from_bytes(occupied, 'little') & 1 == 1:
                    f.seek(20,1)
                    item_slot += 1
                    continue
                f.seek(-4,1)
                # Write item and move to next empty slot
                f.write(0x3F800001.to_bytes(4, 'little'))
                f.seek(4,1)
                f.write(int(item_type).to_bytes(4, 'little'))
                f.write(item_list[index].to_bytes(4, 'little'))
                f.write(item_list[index].to_bytes(4, 'little'))
                f.write(int(item_qty).to_bytes(4, 'little'))
                index += 1
                item_slot += 1
        return 0
    except:
        return 1

def overwriteInventory(filepath, inv_addr, item_list, item_type, item_qty):
    try:
        # Open file
        with open(filepath, 'rb+') as f:
            f.seek(inv_addr)
            item_slot = 0
            index = 0
            while index < len(item_list) and item_slot < 2000:
                occupied = f.read(4)
                if int.from_bytes(occupied, 'little') & 1 == 1:
                    f.seek(4,1)
                    current_item_type = f.read(4)
                    # If a key item, skip to next item slot
                    if int.from_bytes(current_item_type, 'little') == 3:
                        f.seek(12,1)
                        item_slot += 1
                        continue
                    else:
                        f.seek(-8,1)
                f.seek(-4,1)
                # Write item and move to next slot
                f.write(0x3F800001.to_bytes(4, 'little'))
                f.seek(4,1)
                f.write(int(item_type).to_bytes(4, 'little'))
                f.write(item_list[index].to_bytes(4, 'little'))
                f.write(item_list[index].to_bytes(4, 'little'))
                f.write(int(item_qty).to_bytes(4, 'little'))
                index += 1
                item_slot += 1
            return f.tell()
    except:
        raise

def allItems(filepath, inv_addr):
    consumables = list(range(1, 34)) + list(range(50, 59)) + list(range(60, 68)) + list(range(70, 80)) + list(range(90, 92)) \
                    + list(range(100, 107)) + list(range(110, 128)) + list(range(200, 231))
    equipment = list(range(301, 404))
    farm = list(range(501,510)) + list(range(520, 540))
    medals = list(range(1001,1701))
    accessories = [10101, 12401, 10201, 12501, 10301, 10302, 12601, 
                10401, 10501, 10502, 12701, 12702, 12801, 
                12901, 13001, 10701, 10801, 10901, 10902, 
                13101, 13102, 13201, 11001, 11101, 13301, 
                13401, 11201, 11301, 13501, 11401, 11402, 
                11403, 13601, 11501, 11601, 13701, 13801, 
                13901, 11701, 11702, 11703, 14001, 14101, 
                11801, 11802, 14201, 11901, 12001, 12002, 
                12003, 14301, 12101, 12102, 12103, 14401, 
                14402, 14501, 12201, 12301, 12302, 12303]
    
    try:
        offset = overwriteInventory(filepath, inv_addr, consumables, USABLE_ITEM, 95)
        offset = overwriteInventory(filepath, offset, equipment, EQUIP_ITEM, 95)
        offset = overwriteInventory(filepath, offset, farm, FARM_ITEM, 95)
        offset = overwriteInventory(filepath, offset, medals, MEDAL_ITEM, 1)
        overwriteInventory(filepath, offset, accessories, ACCESSORY_ITEM, 95)
        return 0
    except:
        return 1

def write32(filepath, addr, value):
    try:
        with open(filepath, 'rb+') as f:
            f.seek(addr)
            f.write(int(value).to_bytes(4, 'little'))
        return 0
    except:
        return 1

def main():
    print('\n\n==== Digimon Story Cyber Sleuth: Complete Edition Save Editor ====\n')
    ret = 0
    if len(argv) > 1:
        filepath = argv[1]
    else:
        print('Path to save file (0000.bin, 0001.bin, etc): ', end='')
        filepath = input()
    print('Choose game to alter\n\n'
        '1) Cyber Sleuth\n'
        '2) Hacker\'s Memory\n'
        '3) Both\n'
        ': ', end='')
    try:
        game = int(input())
    except:
        print('Please input a number.\n\n')
        return 1
    print('\n\nChoose a modification\n'
        'Note: With inventory cheats it\'s best to sell off existing items to\n'
        '      prevent duplicate entries\n\n'
        '1)  Add all medals to inventory                        (700 inventory slots)\n'
        '2)  Add 5 stacks of Popular Guy\'s Guide to inventory     (5 inventory slots)\n'
        '3)  Add 99x of all stat increasing foods to inventory    (7 inventory slots)\n'
        '4)  Add 99x of all stat decreasing items to inventory    (6 inventory slots)\n'
        '5)  Add 99x of all equipable USBs to inventory           (6 inventory slots)\n'
        '6)  Add 50x of all Digimon Accessories to inventory     (61 inventory slots)\n'
        '7)  Complete the Field Guide                            (Affects both games)\n'
        '8)  200% Scan all Digimon                          (Only discovered Digimon)\n'
        '9)  Add 95x of all items                                (Excludes Key Items)\n'
        '10) Max Yen\n'
        '11) Max Party Memory\n'
        '12) 100 Points short of Max Rank\n'
        ': ', end='')
    try:
        cheat = int(input())
    except:
        print('Please input a number.\n\n')
        return 1

    if game not in [1, 2, 3]:
        print('\n\nInvalid game choice\n')
    print('\n\nBacking up save file...')
    try:
        copy2(filepath, filepath+'.bak')
    except:
        print('Could not make backup! Ensure file exists and directory is writable.\n')
        return 1
    if game == 1 or game == 3:
        print('Executing cheat for Cyber Sleuth...')
        if cheat == 1:
            medals = list(range(1001,1701))
            ret = addToInventory(filepath, CS_Inv_Addr, medals, MEDAL_ITEM, 1)
        elif cheat == 2:
            item = [214]
            for _ in range(5):
                ret = addToInventory(filepath, CS_Inv_Addr, item, USABLE_ITEM, 99)
        elif cheat == 3:
            items = range(202, 209)
            ret = addToInventory(filepath, CS_Inv_Addr, items, USABLE_ITEM, 99)
        elif cheat == 4:
            items = [112, 115, 118, 121, 124, 127]
            ret = addToInventory(filepath, CS_Inv_Addr, items, USABLE_ITEM, 99)
        elif cheat == 5:
            equipment = list(range(395, 401))
            ret = addToInventory(filepath, CS_Inv_Addr, equipment, EQUIP_ITEM, 99)
        elif cheat == 6:
            accessories = [10101, 12401, 10201, 12501, 10301, 10302, 12601, 
                10401, 10501, 10502, 12701, 12702, 12801, 
                12901, 13001, 10701, 10801, 10901, 10902, 
                13101, 13102, 13201, 11001, 11101, 13301, 
                13401, 11201, 11301, 13501, 11401, 11402, 
                11403, 13601, 11501, 11601, 13701, 13801, 
                13901, 11701, 11702, 11703, 14001, 14101, 
                11801, 11802, 14201, 11901, 12001, 12002, 
                12003, 14301, 12101, 12102, 12103, 14401, 
                14402, 14501, 12201, 12301, 12302, 12303]  
            ret = addToInventory(filepath, CS_Inv_Addr, accessories, ACCESSORY_ITEM, 50)
        elif cheat == 7:
            try: 
                with open(filepath, 'rb+') as f: 
                    f.seek(0x9CC)
                    for _ in range(351):
                        f.read(4)
                        f.write(int(3).to_bytes(4, 'little'))
                ret = 0
            except:
                ret = 1
        elif cheat == 8:
            try: 
                with open(filepath, 'rb+') as f: 
                    f.seek(CS_DigiConvert_Addr)
                    for _ in range(346):
                        f.read(2)
                        f.write(int(200).to_bytes(2, 'little'))
                ret = 0
            except:
                ret = 1
        elif cheat == 9:
            ret = allItems(filepath, CS_Inv_Addr)
        elif cheat == 10:
            ret = write32(filepath, CS_Money_Addr, 9999999)
        elif cheat == 11:
            ret = write32(filepath, CS_Party_Mem_Addr, 255)
        elif cheat == 12:
            ret = write32(filepath, CS_Rank_Addr, 19)
            ret = write32(filepath, CS_Points_Addr, 49900)
        else:
            print('Invalid cheat choice.\n')

    if game == 2 or game == 3:
        print('Executing cheat for Hacker\'s Memory...')
        if cheat == 1:
            medals = list(range(1001,1701))
            ret = addToInventory(filepath, HM_Inv_Addr, medals, MEDAL_ITEM, 1)
        elif cheat == 2:
            item = [214]
            for _ in range(5):
                ret = addToInventory(filepath, HM_Inv_Addr, item, USABLE_ITEM, 99)
        elif cheat == 3:
            items = list(range(202, 209))
            ret = addToInventory(filepath, HM_Inv_Addr, items, USABLE_ITEM, 99)
        elif cheat == 4:
            items = [112, 115, 118, 121, 124, 127]
            ret = addToInventory(filepath, HM_Inv_Addr, items, USABLE_ITEM, 99)
        elif cheat == 5:
            equipment = list(range(395, 401))
            ret = addToInventory(filepath, HM_Inv_Addr, equipment, EQUIP_ITEM, 99)
        elif cheat == 6:
            accessories = [10101, 12401, 10201, 12501, 10301, 10302, 12601, 
                10401, 10501, 10502, 12701, 12702, 12801, 
                12901, 13001, 10701, 10801, 10901, 10902, 
                13101, 13102, 13201, 11001, 11101, 13301, 
                13401, 11201, 11301, 13501, 11401, 11402, 
                11403, 13601, 11501, 11601, 13701, 13801, 
                13901, 11701, 11702, 11703, 14001, 14101, 
                11801, 11802, 14201, 11901, 12001, 12002, 
                12003, 14301, 12101, 12102, 12103, 14401, 
                14402, 14501, 12201, 12301, 12302, 12303]  
            ret = addToInventory(filepath, HM_Inv_Addr, accessories, ACCESSORY_ITEM, 50)
        elif cheat == 7:
            try: 
                with open(filepath, 'rb+') as f: 
                    f.seek(0x9CC)
                    for _ in range(351):
                        f.read(4)
                        f.write(int(3).to_bytes(4, 'little'))
                ret = 0
            except:
                ret = 1
        elif cheat == 8:
            try: 
                with open(filepath, 'rb+') as f: 
                    f.seek(HM_DigiConvert_Addr)
                    for _ in range(346):
                        f.read(2)
                        f.write(int(200).to_bytes(2, 'little'))
                ret = 0
            except:
                ret = 1
        elif cheat == 9:
            ret = allItems(filepath, HM_Inv_Addr)
        elif cheat == 10:
            ret = write32(filepath, HM_Money_Addr, 9999999)
        elif cheat == 11:
            ret = write32(filepath, HM_Party_Mem_Addr, 255)
        elif cheat == 12:
            ret = write32(filepath, HM_Rank_Addr, 19)
            ret = write32(filepath, HM_Points_Addr, 49900)
        else:
            print('Invalid cheat choice.\n')
    
    if ret == 0:
        print('Clearing backup...')
        try:
            remove(filepath+'.bak')
        except:
            print('Could not remove backup file. Remove manually.')
        print('Done!\n')
    if ret > 0:
        print('An error has occured applying cheats. Please check that the file exists, is writable, and is not corrupted.\n'
            'Restoring backed up save...')
        try:
            copy2(filepath+'.bak', filepath)
            print('Backup restored successfully.\n')
        except:
            print('Could not restore backup file. Please manually rename backup file.\n')
    return ret

if __name__ == "__main__":
    exit(main())   

# # All Medals Obtained (Unconfirmed)
# with open('0000.bin', 'rb+') as f:
#     data = b'\xFE\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF'\
#             b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF'\
#             b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF'\
#             b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF'\
#             b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF'\
#             b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF'\
#             b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF'\
#             b'\xFF\xFF\xFF\x1F'
#     #Cyber Sleuth
#     f.seek(0x1958)
#     f.write(data)
