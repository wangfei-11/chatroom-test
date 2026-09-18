package com.chatroom.login;

import com.chatroom.common.BaseTest;
import org.junit.Assert;
import org.junit.Test;
import org.openqa.selenium.Alert;
import org.openqa.selenium.By;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

import java.time.Duration;

public class LoginTest extends BaseTest {

    // 用例1：登录成功 → 弹"登录成功！" → 跳转 client.html
    @Test
    public void testLoginSuccess() {
        driver.get(BASE_URL + "/login.html");
        driver.findElement(By.id("username")).sendKeys("zhangsan");
        driver.findElement(By.id("password")).sendKeys("123");
        driver.findElement(By.id("submit")).click();

        Alert alert = waitForAlert();
        Assert.assertEquals("登录成功！", alert.getText());
        alert.accept();

        // 显式等待：最多等 5 秒，URL 变成 client.html
        new WebDriverWait(driver, Duration.ofSeconds(5))
                .until(ExpectedConditions.urlContains("client.html"));
        Assert.assertTrue("登录成功后未跳转 client.html",
                driver.getCurrentUrl().contains("client.html"));
    }

    // 用例2：密码错误 → 弹"用户名或密码错误" → 留在登录页
    @Test
    public void testLoginWrongPassword() {
        driver.get(BASE_URL + "/login.html");
        driver.findElement(By.id("username")).sendKeys("zhangsan");
        driver.findElement(By.id("password")).sendKeys("wrong123");
        driver.findElement(By.id("submit")).click();

        Alert alert = waitForAlert();
        Assert.assertEquals("用户名或密码错误", alert.getText());
        alert.accept();
        Assert.assertTrue(driver.getCurrentUrl().contains("login.html"));
    }

    // 用例3：用户名密码为空 → 弹"当前输入的用户名或密码为空！"
    @Test
    public void testLoginEmpty() {
        driver.get(BASE_URL + "/login.html");
        driver.findElement(By.id("submit")).click();

        Alert alert = waitForAlert();
        Assert.assertEquals("当前输入的用户名或密码为空！", alert.getText());
        alert.accept();
    }
}
