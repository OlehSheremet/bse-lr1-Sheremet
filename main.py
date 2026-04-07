import sys
import os
from PremCheck import PremiumCheck

def main():
    details = input("Enter your details: ")
    premium_details = "i3kUY872nO9A"
    
    if PremiumCheck(details, premium_details):
        print("Access granted to premium features.")
    else:
        print("Access denied. Please upgrade to premium.")