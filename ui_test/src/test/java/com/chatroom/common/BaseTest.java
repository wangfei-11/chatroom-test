package com.chatroom.common;

import org.junit.After;
import org.junit.Before;
import org.openqa.selenium.Alert;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

import java.time.Duration;

/**
 * 测试基类：每个用例自动开一个浏览器，跑完自动关
 */
public abstract class BaseTest {

    protected static final String BASE_URL = UiHelper.BASE_URL;
    protected WebDriver driver;

    @Before
    public void setUp() {
        driver = new ChromeDriver();
        // 隐式等待：找不到元素时最多等 5 秒
        driver.manage().timeouts().implicitlyWait(Duration.ofSeconds(5));
    }

    @After
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }

    // 等待弹窗出现（最多 5 秒），避免 ajax 异步弹窗的时序竞态
    protected Alert waitForAlert() {
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(5));
        return wait.until(ExpectedConditions.alertIsPresent());
    }
}
