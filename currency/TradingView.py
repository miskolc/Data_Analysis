from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import lxml.html
from Database import Database
from lxml import etree

from DefaultVariables import *
import Helper
import os, sys, os
import time

class TradingView:

    def __init__(self):
        print "init Crawler"
        firefox_profile = webdriver.FirefoxProfile()
        firefox_profile.set_preference("javascript.enabled", False)
        self.driver = webdriver.Firefox(firefox_profile=firefox_profile)
        self.driver.set_window_size(1200, 800)

        try:
            self.driver.get(DEFAULT_IQOPTION_URL)
        except Exception as e:
            print "connection failed"
            print e

    def login(self):
        self.driver.find_element_by_xpath("//div[@class='header__btn header__btn_sign btn_transparent js-login-btn']").click()
        time.sleep(3)
        login_form = self.driver.find_element_by_id("loginFrm")
        login_form.find_element_by_name("email").send_keys("likedan5@icloud.com")
        login_form.find_element_by_name("password").send_keys("Diyici140726")
        login_form.find_element_by_xpath("//button[@class='btn-submit input-form__btn input-form__btn_green']").click()
        time.sleep(2)
        self.driver.find_element_by_xpath("//div[@class='profile__trade js-btn-trade']").click()
        time.sleep(15)

    def trade_down(self):
        element = self.driver.find_element_by_id("glcanvas")
        action = webdriver.common.action_chains.ActionChains(self.driver)
        action.move_to_element(element).move_by_offset(550, 240).click().perform()

    def trade_up(self):
        element = self.driver.find_element_by_id("glcanvas")
        action = webdriver.common.action_chains.ActionChains(self.driver)
        action.move_to_element(element).move_by_offset(550, 120).click().perform()

    def quit(self):
        self.driver.quit()