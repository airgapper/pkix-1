#!/usr/bin/python3

from database import PKIXDatabase

db = PKIXDatabase("mongodb://localhost:27017")

def main():
    try:
        cmd = input("pkix » ")
    except KeyboardInterrupt:
        exit()

    cmd = cmd.split()
    try:
        cmdi = cmd[0]
    except IndexError:
        cmdi = cmd

    if cmdi == "help":
        print("\033[4mPKTF cli v1.0\033[0m")
        print("help             Show this help menu")
        print("init             Initialize the network")
        print("reload <ASN>     Reload from PeeringDB")
        print("add <ASN>        Add from PeeringDB")
        print("reset            Reset the network (DANGER)")

    elif cmdi == "show":
        print()
        for member in db._members.find().sort("suffix"):
            print("\033[3m" + member["name"] + "\033[0m \033[4mAS" + member["asn"] + "\033[0m")
            print("  \033[2m" + db.ipv4().strip("0/24") + str(member["suffix"]) + "\033[0m")
            print("  \033[2m" + db.ipv6().strip("/64") + str(member["suffix"]) + "\033[0m")
        print()

    elif cmdi == "reload":
        db.reload(cmd[1])

    elif cmdi == "add":
        db.add(cmd[1], input("Speed: "), input("Email: "))

    elif cmdi == "reset":
        if input("Are you sure you want to reset? [y/N] ") in ["y", "Y"]:
            db.reset()

    elif cmdi == "init":
        db.init(input("Name: "), input("ASN: "), input("Site: "), input("IPv4: "), input("IPv6: "))

    main()
main()
