'''
UBC Eye Movement Data Analysys Toolkit
Created on 2011-08-25

@author: skardan
'''
from data_structures import Fixation
import params
import math


def point_inside_polygon(x,y,poly):
    """Determines if a point is inside a given polygon or not
    
        The algorithm is called "Ray Casting Method".
        
    Args:
        poly: is a list of (x,y) pairs defining the polgon 
        
    Returns:
        True or False.
    """
    n = len(poly)
    
    if n==0:
        return False
    
    inside = False

    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x,p1y = p2x,p2y

    return inside   

def get_chunk(data, ind, start, end):
    """
    Args:
        data: 
        ind
        start
        end
        
    Returns:
        curr_ind
        start_ind
        end_ind
    """
    datalen = len(data)
    curr_ind = ind
    if isinstance(data[curr_ind],Fixation): #if it is a fixation
        if params.INCLUDE_HALF_FIXATIONS: 
            while curr_ind < datalen and data[curr_ind].timestamp < start:
                curr_ind += 1
        
            if data[curr_ind-1].fixationduration!= None: # if the last fixation before, is mostly in this segment
                if (data[curr_ind-1].timestamp + (data[curr_ind-1].fixationduration)/2.0) > start:
                    curr_ind -=1
            start_ind = curr_ind
            while curr_ind < datalen and (data[curr_ind].timestamp + (data[curr_ind].fixationduration)) <= end:
                curr_ind += 1
        
             
            if curr_ind == start_ind:   # a no point chunk!
                end_ind = curr_ind -1
            elif data[curr_ind-1].fixationduration!= None: # if the last fixation is mostly outside this segment
                if (data[curr_ind-1].timestamp + (data[curr_ind-1].fixationduration)/2.0) > end:
                    end_ind = curr_ind - 2 
                else: 
                    end_ind = curr_ind -1
            else:
                end_ind = curr_ind -1
        else:   #No half fixation inclusion
            while curr_ind < datalen and data[curr_ind].timestamp < start:
                curr_ind += 1
        
            start_ind = curr_ind
            while curr_ind < datalen and (data[curr_ind].timestamp + (data[curr_ind].fixationduration)) <= end:
                curr_ind += 1
        
             
            if curr_ind == start_ind:   # a no point chunk!
                end_ind = curr_ind -1
            elif data[curr_ind-1].fixationduration!= None: # if the last fixation is mostly outside this segment
                if (data[curr_ind-1].timestamp + (data[curr_ind-1].fixationduration)/2.0) > end:
                    end_ind = curr_ind - 2 
                else: 
                    end_ind = curr_ind -1
            else:
                end_ind = curr_ind -1            
    else:
        while curr_ind < datalen and data[curr_ind].timestamp < start:
            curr_ind += 1
    
        start_ind = curr_ind
        while curr_ind < datalen and data[curr_ind].timestamp <= end:
            curr_ind += 1
    
        end_ind = curr_ind -1
    
    end_ind +=1 #because the last index is not inclusive in pythond!
    return curr_ind, start_ind, end_ind

def stddev(data):
    """Returns the standard deviation of a list of numbers
    
    Args:
        data: a list of numbers
    
    returns:
        a float that is the std deviation of the list of numbers or NAN if it is undefined
    """
    if len(data)< 2:
        return float('nan')
    m = mean(data)
    return math.sqrt(sum(map(lambda x: (x-m)**2, data))/float(len(data)-1))
    
def mean(data):
    """Returns the average of a list of numbers
    
    Args:
        data: a list of numbers
    
    returns:
        a float that is the average of the list of numbers
    """
    if len(data)==0:
        return 0
    return sum(data) / float(len(data))