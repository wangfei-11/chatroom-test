package com.chatroom.register;

import com.chatroom.common.BaseTest;
import org.junit.Assert;
import org.junit.Test;
import org.openqa.selenium.Alert;
import org.openqa.selenium.By;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

import java.time.Duration;

public class RegisterTest extends BaseTest {

    // 生成随机测试账号，test_ 前缀，不污染已有数据
    // 注意：username 数据库限制 varchar(20)，所以只取 UUID 前 8 位
    private String randomUsername() {
        return "tu_" + java.util.UUID.randomUUID().toString().substring(0, 8);
    }

    // 用例1：注册成功 → 弹"注册成功！" → 跳回 login.html
    @Test
    public void testRegisterSuccess() {
        driver.get(BASE_URL + "/register.html");
        driver.findElement(By.id("username")).sendKeys(randomUsername());
        driver.findElement(By.id("password")).sendKeys("123456");
        driver.findElement(By.id("submit")).click();

        Alert alert = waitForAlert();
        Assert.assertEquals("注册成功！", alert.getText());
        alert.accept();

        new WebDriverWait(driver, Duration.ofSeconds(5))
                .until(ExpectedConditions.urlContains("login.html"));
        Assert.assertTrue("注册成功后未跳转 login.html",
                driver.getCurrentUrl().contains("login.html"));
    }

    // 用例2：重复用户名 → 弹"用户名已存在" → 留在注册页
    @Test
    public void testRegisterDuplicateUsername() {
        String username = randomUsername();

        // 第一次注册，成功
        driver.get(BASE_URL + "/register.html");
        driver.findElement(By.id("username")).sendKeys(username);
        driver.findElement(By.id("password")).sendKeys("123456");
        driver.findElement(By.id("submit")).click();
        Alert firstAlert = waitForAlert();
        Assert.assertEquals("注册成功！", firstAlert.getText());
        firstAlert.accept();

        // 回到注册页，用同一个用户名再注册一次
        driver.get(BASE_URL + "/register.html");
        driver.findElement(By.id("username")).sendKeys(username);
        driver.findElement(By.id("password")).sendKeys("123456");
        driver.findElement(By.id("submit")).click();

        Alert secondAlert = waitForAlert();
        Assert.assertEquals("用户名已存在", secondAlert.getText());
        secondAlert.accept();
        Assert.assertTrue(driver.getCurrentUrl().contains("register.html"));
    }

    // 用例3：用户名密码为空 → 弹"当前输入的用户名或密码为空！"
    @Test
    public void testRegisterEmpty() {
        driver.get(BASE_URL + "/register.html");
        driver.findElement(By.id("submit")).click();

        Alert alert = waitForAlert();
        Assert.assertEquals("当前输入的用户名或密码为空！", alert.getText());
        alert.accept();
    }
}
