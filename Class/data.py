from math import sin, cos, sqrt, atan2, radians
import time

class Data:

    def getClosestPoP(self,latitude,longitude,pops):
        lowest,ip = 0,""
        for pop in pops:
            if int(time.time()) - 60 > pop[4]: continue # ignore fallen nodes
            # Source https://stackoverflow.com/questions/19412462/getting-distance-between-two-points-based-on-latitude-longitude
            # approximate radius of earth in km
            R = 6373.0

            dlon = radians(pop[2]) - radians(longitude)
            dlat = radians(pop[1]) - radians(latitude)

            a = sin(dlat / 2)**2 + cos(radians(latitude)) * cos(radians(pop[1])) * sin(dlon / 2)**2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))

            distance = R * c
            if distance < lowest or lowest == 0:
                lowest,ip = distance,pop[3]
        return ip
