package com.chatroom.common;

import org.openqa.selenium.Alert;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

import java.time.Duration;
import java.util.UUID;

/**
 * UI 公共操作：注册、登录、等弹窗、随机账号
 */
public class UiHelper {

    public static final String BASE_URL = "http://localhost:8080";

    // 随机测试账号，test_ 前缀不污染已有数据；username 限制 varchar(20)
    public static String randomUsername() {
        return "tu_" + UUID.randomUUID().toString().substring(0, 8);
    }

    // 等待弹窗出现（最多 5 秒），避免 ajax 异步弹窗的时序竞态
    public static Alert waitAlert(WebDriver driver) {
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(5));
        return wait.until(ExpectedConditions.alertIsPresent());
    }

    // 注册：成功后停在 login.html
    public static void register(WebDriver driver, String username, String password) {
        driver.get(BASE_URL + "/register.html");
        driver.findElement(By.id("username")).sendKeys(username);
        driver.findElement(By.id("password")).sendKeys(password);
        driver.findElement(By.id("submit")).click();
        waitAlert(driver).accept();
        new WebDriverWait(driver, Duration.ofSeconds(5))
                .until(ExpectedConditions.urlContains("login.html"));
    }

    // 登录：成功后停在 client.html
    public static void login(WebDriver driver, String username, String password) {
        driver.get(BASE_URL + "/login.html");
        driver.findElement(By.id("username")).sendKeys(username);
        driver.findElement(By.id("password")).sendKeys(password);
        driver.findElement(By.id("submit")).click();
        waitAlert(driver).accept();
        new WebDriverWait(driver, Duration.ofSeconds(5))
                .until(ExpectedConditions.urlContains("client.html"));
    }

    // 完整加好友：A 发申请（driverA 需已登录）→ B 登录接受
    public static void makeFriends(WebDriver driverA, String userB, WebDriver driverB) {
        driverA.findElement(By.id("searchInput")).sendKeys(userB);
        driverA.findElement(By.id("searchBtn")).click();
        new WebDriverWait(driverA, Duration.ofSeconds(5))
                .until(ExpectedConditions.visibilityOfElementLocated(
                        By.cssSelector("#search-result-list li")));
        driverA.findElement(By.cssSelector(".add-friend-btn")).click();
        Alert prompt = waitAlert(driverA);
        prompt.sendKeys("UI自动化测试");
        prompt.accept();
        waitAlert(driverA).accept(); // 实际弹"操作成功"

        login(driverB, userB, "123456");
        driverB.findElement(By.id("showPendingRequestsBtn")).click();
        new WebDriverWait(driverB, Duration.ofSeconds(5))
                .until(ExpectedConditions.visibilityOfElementLocated(
                        By.cssSelector("#pendingRequestModal .accept-btn")));
        driverB.findElement(By.cssSelector("#pendingRequestModal .accept-btn")).click();
        waitAlert(driverB).accept(); // "操作成功"
    }
}
