package com.chatroom.message;

import com.chatroom.common.BaseTest;
import com.chatroom.common.UiHelper;
import org.junit.Assert;
import org.junit.Test;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.support.ui.WebDriverWait;

import java.time.Duration;

public class MessageTest extends BaseTest {

    // 前置：注册 A、B，A、B 都登录并加为好友；A 点 B 建好会话（accept 掉已知缺陷弹窗）
    // 返回 userA / userB / B 的浏览器（保持打开，验证实时收消息）
    private Object[] prepareSession() {
        String userA = UiHelper.randomUsername();
        String userB = UiHelper.randomUsername();
        UiHelper.register(driver, userA, "123456");
        UiHelper.login(driver, userA, "123456");

        WebDriver driverB = new ChromeDriver();
        driverB.manage().timeouts().implicitlyWait(Duration.ofSeconds(5));
        UiHelper.register(driverB, userB, "123456");
        UiHelper.makeFriends(driver, userB, driverB);

        // A 刷新拉好友列表，点好友 B 创建会话
        driver.navigate().refresh();
        driver.findElement(By.cssSelector(".tab .tab-friend")).click();
        WebElement friendLi = new WebDriverWait(driver, Duration.ofSeconds(5))
                .until(d -> d.findElements(By.cssSelector("#friend-list li")).stream()
                        .filter(li -> li.getText().equals(userB))
                        .findFirst().orElse(null));
        friendLi.click();
        // 已知缺陷：先 click 后 createSession，弹"参数类型错误：sessionId"，accept 掉
        waitForAlert().accept();
        new WebDriverWait(driver, Duration.ofSeconds(5))
                .until(d -> d.findElements(By.cssSelector("#session-list li")).stream()
                        .anyMatch(li -> li.getAttribute("message-session-id") != null
                                && li.findElement(By.tagName("h3")).getText().equals(userB)));

        return new Object[]{userA, userB, driverB};
    }

    // 用例1：A 发消息 → A 消息区回显，B 实时收到（会话列表预览更新）
    @Test
    public void testSendMessage() {
        Object[] prep = prepareSession();
        String userA = (String) prep[0];
        String userB = (String) prep[1];
        WebDriver driverB = (WebDriver) prep[2];
        String content = "hi" + (System.currentTimeMillis() % 100000);
        try {
            driver.findElement(By.cssSelector(".right .message-input")).sendKeys(content);
            driver.findElement(By.cssSelector(".right .ctrl button")).click();

            // A 的消息区出现刚发的消息
            new WebDriverWait(driver, Duration.ofSeconds(5))
                    .until(d -> d.findElements(By.cssSelector(".right .message-show p")).stream()
                            .anyMatch(p -> p.getText().equals(content)));

            // B 的会话列表出现 A 的会话，且预览内容包含该消息
            new WebDriverWait(driverB, Duration.ofSeconds(5))
                    .until(d -> d.findElements(By.cssSelector("#session-list li")).stream()
                            .anyMatch(li -> li.findElement(By.tagName("h3")).getText().equals(userA)
                                    && li.findElement(By.tagName("p")).getText().contains(content)));
        } finally {
            driverB.quit();
        }
    }

    // 用例2：输入框为空点发送 → 不发消息，消息区无新增
    @Test
    public void testSendEmptyMessage() {
        Object[] prep = prepareSession();
        WebDriver driverB = (WebDriver) prep[2];
        try {
            driver.findElement(By.cssSelector(".right .ctrl button")).click();

            // 空消息 JS 直接 return，消息区应没有任何消息
            Assert.assertEquals("空消息不应发送",
                    0, driver.findElements(By.cssSelector(".right .message-show .message")).size());
        } finally {
            driverB.quit();
        }
    }
}
