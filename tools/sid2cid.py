from otbxml2xml import items

while True:
    try:
        num = raw_input("Sid: ")
    except:
        break
    parts = num.split(',')
    nums = []

    for part in parts:
        num = int(part.strip())
        nums.append(str(items[num].cid))

    print ', '.join(nums)
    
