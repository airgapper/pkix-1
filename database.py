import requests
import pymongo


class PKIXDatabase:
    def __init__(self, mongo_uri):
        self._client = pymongo.MongoClient(mongo_uri)
        self._db = self._client["pkix"]

        self._network = self._db["network"]
        self._members = self._db["members"]

    def site(self):
        return self._network.find_one()["site"]

    def ipv4(self):
        return self._network.find_one()["ipv4"] + "0/24"

    def ipv6(self):
        return self._network.find_one()["ipv6"] + "/64"

    def init_rs():
        self._members.insert_one({
            "asn": asn,
            "name": "Route Server 1",
            "site": self.site(),
            "speed": "1G",
            "email": "",
            "suffix": 253,
            "website": "",
            "as-set": ""
        })

        self._members.insert_one({
            "asn": asn,
            "name": "Route Server 2",
            "site": self.site(),
            "speed": "1G",
            "email": "",
            "suffix": 254,
            "website": "",
            "as-set": ""
        })

    def init(self, name, asn, site, ipv4, ipv6):
        self._network.insert_one({
            "name": name,
            "asn": asn,
            "site": site,
            "ipv4": ipv4,
            "ipv6": ipv6,
            "next_ip": 2
        })

        init_rs()

    def reset(self):
        self._members.drop()
        self._network.update_one({}, {"$set": {"next_ip": 2}})
        asn = self._network.find_one({})["asn"]

        init_rs()

    def add(self, asn, speed, email):
        next_ip = self._network.find_one()["next_ip"]

        try:
            peeringdb = requests.get("https://peeringdb.com/api/net?asn=" + str(asn)).json()["data"][0]
        except IndexError:
            peeringdb = {
                "name": "",
                "website": "",
                "irr_as_set": ""
            }

        self._members.insert_one({
            "asn": str(asn),
            "name": peeringdb["name"],
            "site": self.site(),
            "speed": speed,
            "email": email,
            "suffix": next_ip,
            "website": peeringdb["website"],
            "as-set": peeringdb["irr_as_set"]
        })

        # Increment next_ip
        self._network.update_one({}, {"$inc": {"next_ip": 1}})

    def reload(self, asn):
        try:
            peeringdb = requests.get("https://peeringdb.com/api/net?asn=" + str(asn)).json()["data"][0]
        except IndexError:
            peeringdb = {
                "name": "",
                "website": "",
                "irr_as_set": ""
            }

        self._members.update_one({"asn": str(asn)}, {"$set": {
                                                                "name": peeringdb["name"],
                                                                "website": peeringdb["website"],
                                                                "as-set": peeringdb["irr_as_set"]
                                                            }})

    def members_html(self):
        html = ""
        for member in self._members.find().sort("suffix"):
            html += """<tr>
                        <td><a href='""" + member["website"] + """'>""" + member["name"] + """</a></td>
                        <td><a href='https://bgp.he.net/""" + member["asn"] + """'>AS""" + member["asn"] + """</a></td>
                        <td>""" + member["site"] + """</td>
                        <td>""" + member["speed"] + """</td>
                        <td>""" + self._network.find_one()["ipv4"] + str(member["suffix"]) + """</td>
                        <td>""" + self._network.find_one()["ipv6"] + str(member["suffix"]) + """</td>
                      </tr>"""
        return html
