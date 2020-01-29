#!/usr/bin/env python3
# Author: AnalogMan
# Modified Date: 2020-01-28
# Purpose: Applies various edits to a Digimon Story Cyber Sleuth Complete Edition for Nintento Switch save file
# Usage: DigmonSaveEditor.py

from sys import version_info, argv
if version_info <= (3,2,0):
    print('\nPython version 3.2.0+ needed to run this script.')
    exit(1)

from os import remove
from shutil import copy2
import struct

CS_Inv_Addr = 0x3EB30
HM_Inv_Addr = 0xA02D0
USABLE_ITEM = 0; EQUIP_ITEM = 1; FARM_ITEM = 2; KEY_ITEM = 3; MEDAL_ITEM = 4; ACCESSORY_ITEM = 5

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

CYBER_SLEUTH = 1; HACKERS_MEMORY = 2

# Struct(occupied, item slot, item type, item number, item number, quantity)
item_data = struct.Struct('< I I I I I I')

# All current valid items except key items
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

# Reads inventory from file and returns full inventory and currently obtained item IDs
def buildInventory(filepath, inv_addr):
    inventory = []
    values = []
    existing_items = []
    try:
        # Open file and read full inventory into list
        with open(filepath, 'rb') as f:
            f.seek(inv_addr)
            for _ in range(2000):
                values = list(item_data.unpack(f.read(24)))
                inventory.append(values)
    except:
        raise

    # Iterate through inventory and adding item ID to list
    i = 0
    while i < 2000:
        if inventory[i][0] & 1 == 1:
            existing_items.append(inventory[i][3])
        i += 1
    return inventory, existing_items

# Reads inventory, seeks to first empty slot, adds passed item then writes new inventory back
def addToInventory(filepath, inv_addr, item_list, item_type, item_qty, duplicate=False):
    inventory, _ = buildInventory(filepath, inv_addr)
    skip_items = []
    if duplicate == False:
        for item in inventory:
            if item[0] & 1 == 1:
                if item[3] in item_list:
                    item[5] = (item[5] & 0xFFFFFF00) + item_qty
                    skip_items.append(item[3]) 
    i = 0
    while i < 2000:
        if inventory[i][0] & 1 == 0:
            for item in item_list:
                if item not in skip_items:
                    inventory[i] = [0x3F800001, i, item_type, item, item, item_qty]
                    i +=1
            break
        i += 1
    
    try:
        with open(filepath, 'rb+') as f:
            f.seek(inv_addr)
            for item in inventory:
                f.write(item_data.pack(*item))
        return 0
    except:
        return 1

# Increases all item quantities except Key Items and Medals to 95, 
# then finds empty space and adds remaining missing items
def overwriteInventory(inventory, existing_items):       
    i = 0
    while i < 2000:
        if inventory[i][0] & 1 == 1:
            if inventory[i][2] != KEY_ITEM and inventory[i][2] != MEDAL_ITEM:
                inventory[i][5] = (inventory[i][5] & 0xFFFFFF00) + 95

        if inventory[i][0] & 1 == 0:
            for item in consumables:
                if item not in existing_items:
                    inventory[i] = [0x3F800001, i, USABLE_ITEM, item, item, 95]
                    i += 1
            for item in equipment:
                if item not in existing_items:
                    inventory[i] = [0x3F800001, i, EQUIP_ITEM, item, item, 95]
                    i += 1
            for item in farm:
                if item not in existing_items:
                    inventory[i] = [0x3F800001, i, FARM_ITEM, item, item, 95]
                    i += 1
            for item in medals:
                if item not in existing_items:
                    inventory[i] = [0x3F800001, i, MEDAL_ITEM, item, item, 1]
                    i += 1
            for item in accessories:
                if item not in existing_items:
                    inventory[i] = [0x3F800001, i, ACCESSORY_ITEM, item, item, 95]
                    i += 1
            break
        i += 1
    return inventory

def allItems(filepath, inv_addr):
    inventory, existing_items = buildInventory(filepath, inv_addr)
    data = overwriteInventory(inventory, existing_items)
    try:
        with open(filepath, 'rb+') as f:
            f.seek(inv_addr)
            for item in data:
                f.write(item_data.pack(*item))
        return 0
    except:
        return 1

def write32(filepath, addr, value):
    try:
        with open(filepath, 'rb+') as f:
            f.seek(addr)
            f.write(struct.pack('< I', value))
        return 0
    except:
        return 1

def write16(filepath, addr, value):
    try:
        with open(filepath, 'rb+') as f:
            f.seek(addr)
            f.write(struct.pack('< H', value))
        return 0
    except:
        return 1

def main():
    global medals
    global equipment
    global accessories

    print('\n\n==== Digimon Story Cyber Sleuth: Complete Edition Save Editor ====\n')
    ret = 0
    if len(argv) > 1:
        filepath = argv[1]
    else:
        filepath = input('Path to save file (0000.bin, 0001.bin, etc): ')
    try:
        game = int(input('Choose game to alter\n\n'
        '1) Cyber Sleuth\n'
        '2) Hacker\'s Memory\n'
        '3) Both\n'
        ': '))
    except:
        print('Please input a number.\n\n')
        return 1

    if game not in [CYBER_SLEUTH, HACKERS_MEMORY, CYBER_SLEUTH + HACKERS_MEMORY]:
        print('\n\nInvalid game choice\n')
        return 1

    try:
        cheat = int(input('\n\nChoose a modification\n\n'
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
        ': '))
    except:
        print('Please input a number.\n\n')
        return 1

    print('\n\nBacking up save file...')
    try:
        copy2(filepath, filepath+'.bak')
    except:
        print('Could not make backup! Ensure file exists and directory is writable.\n')
        return 1
        
    if game == CYBER_SLEUTH or game == (CYBER_SLEUTH + HACKERS_MEMORY):
        print('Executing cheat for Cyber Sleuth...')
        if cheat == 1:
            ret = addToInventory(filepath, CS_Inv_Addr, medals, MEDAL_ITEM, 1)
        elif cheat == 2:
            item = [214]
            for _ in range(5):
                ret = addToInventory(filepath, CS_Inv_Addr, item, USABLE_ITEM, 99, True)
        elif cheat == 3:
            items = range(202, 209)
            ret = addToInventory(filepath, CS_Inv_Addr, items, USABLE_ITEM, 99)
        elif cheat == 4:
            items = [112, 115, 118, 121, 124, 127]
            ret = addToInventory(filepath, CS_Inv_Addr, items, USABLE_ITEM, 99)
        elif cheat == 5:
            ret = addToInventory(filepath, CS_Inv_Addr, equipment, EQUIP_ITEM, 99)
        elif cheat == 6: 
            ret = addToInventory(filepath, CS_Inv_Addr, accessories, ACCESSORY_ITEM, 50)
        elif cheat == 7:
            offset = 0x9CC
            for _ in range(351):
                offset += 4
                ret = write32(filepath, offset, 3)
                offset += 4
        elif cheat == 8:
            offset = CS_DigiConvert_Addr
            for _ in range(346):
                offset += 2
                ret = write16(filepath, offset, 200)
                offset += 2
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
            return 1

    if game == HACKERS_MEMORY or game == (CYBER_SLEUTH + HACKERS_MEMORY):
        print('Executing cheat for Hacker\'s Memory...')
        if cheat == 1:
            ret = addToInventory(filepath, HM_Inv_Addr, medals, MEDAL_ITEM, 1)
        elif cheat == 2:
            item = [214]
            for _ in range(5):
                ret = addToInventory(filepath, HM_Inv_Addr, item, USABLE_ITEM, 99, True)
        elif cheat == 3:
            items = list(range(202, 209))
            ret = addToInventory(filepath, HM_Inv_Addr, items, USABLE_ITEM, 99)
        elif cheat == 4:
            items = [112, 115, 118, 121, 124, 127]
            ret = addToInventory(filepath, HM_Inv_Addr, items, USABLE_ITEM, 99)
        elif cheat == 5:
            ret = addToInventory(filepath, HM_Inv_Addr, equipment, EQUIP_ITEM, 99)
        elif cheat == 6: 
            ret = addToInventory(filepath, HM_Inv_Addr, accessories, ACCESSORY_ITEM, 50)
        elif cheat == 7:
            offset = 0x9CC
            for _ in range(351):
                offset += 4
                ret = write32(filepath, offset, 3)
                offset += 4
        elif cheat == 8:
            offset = HM_DigiConvert_Addr
            for _ in range(346):
                offset += 2
                ret = write16(filepath, offset, 200)
                offset += 2
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
            return 1
    
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
            remove(filepath+'.bak')
        except:
            print('Could not restore backup file. Please manually rename backup file.\n')

    return ret

if __name__ == "__main__":
    ret = main()
    input('Press ENTER to quit')
    exit(ret)
