package com.chatroom.smoke;

import org.junit.Assert;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;

/**
 * 环境冒烟：验证 ChromeDriver 能打开登录页
 */
public class SmokeTest {

    @Test
    public void openLoginPage() {
        WebDriver driver = new ChromeDriver();
        try {
            driver.get("http://localhost:8080/login.html");
            System.out.println("页面标题: " + driver.getTitle());
            Assert.assertTrue("未打开登录页，当前URL: " + driver.getCurrentUrl(),
                    driver.getCurrentUrl().contains("login.html"));
            System.out.println("冒烟通过：登录页打开成功");
        } finally {
            driver.quit();
        }
    }
}
