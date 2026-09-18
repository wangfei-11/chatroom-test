package com.chatroom.session;

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
import java.util.List;

public class SessionTest extends BaseTest {

    // 前置：注册 A、B 并建立好友关系（A 的浏览器留在 client.html）
    private String[] prepareFriends() {
        String userA = UiHelper.randomUsername();
        String userB = UiHelper.randomUsername();
        UiHelper.register(driver, userA, "123456");
        UiHelper.login(driver, userA, "123456");
        WebDriver driverB = new ChromeDriver();
        driverB.manage().timeouts().implicitlyWait(Duration.ofSeconds(5));
        try {
            UiHelper.register(driverB, userB, "123456");
            UiHelper.makeFriends(driver, userB, driverB);
        } finally {
            driverB.quit();
        }
        // 好友关系是在 A 页面加载之后建立的，刷新页面重新拉取好友列表
        driver.navigate().refresh();
        return new String[]{userA, userB};
    }

    // 会话列表中 h3 名称为 name 的 li
    private List<WebElement> sessionLisByName(String name) {
        return driver.findElements(By.cssSelector("#session-list li")).stream()
                .filter(li -> li.findElement(By.tagName("h3")).getText().equals(name))
                .collect(java.util.stream.Collectors.toList());
    }

    // 用例1：点击好友 → 自动创建会话，会话列表出现该好友且拿到 sessionId
    @Test
    public void testCreateSessionByClickingFriend() {
        String[] users = prepareFriends();
        String userB = users[1];

        // 切到好友标签，点击好友 B（点击后会自动切回会话标签并创建会话）
        driver.findElement(By.cssSelector(".tab .tab-friend")).click();
        WebElement friendLi = new WebDriverWait(driver, Duration.ofSeconds(5))
                .until(d -> d.findElements(By.cssSelector("#friend-list li")).stream()
                        .filter(li -> li.getText().equals(userB))
                        .findFirst().orElse(null));
        friendLi.click();

        // 已知缺陷：clickFriend 先 click 后 createSession，sessionId 未设置就拉历史消息，
        // 弹"参数类型错误：sessionId"，真实用户也会看到（待修复），测试先 accept 掉
        waitForAlert().accept();

        // 等会话 li 拿到 message-session-id（创建会话的 ajax 是异步的）
        WebElement sessionLi = new WebDriverWait(driver, Duration.ofSeconds(5))
                .until(d -> sessionLisByName(userB).stream()
                        .filter(li -> li.getAttribute("message-session-id") != null)
                        .findFirst().orElse(null));

        String sessionId = sessionLi.getAttribute("message-session-id");
        Assert.assertTrue("会话应拿到有效的 sessionId",
                Integer.parseInt(sessionId) > 0);
        System.out.println("创建会话成功, sessionId: " + sessionId);
    }

    // 用例2：再次点击同一好友 → 不重复创建会话（复用已有会话）
    @Test
    public void testReclickFriendNoDuplicateSession() {
        String[] users = prepareFriends();
        String userB = users[1];

        // 第一次点击好友创建会话
        driver.findElement(By.cssSelector(".tab .tab-friend")).click();
        WebElement friendLi = new WebDriverWait(driver, Duration.ofSeconds(5))
                .until(d -> d.findElements(By.cssSelector("#friend-list li")).stream()
                        .filter(li -> li.getText().equals(userB))
                        .findFirst().orElse(null));
        friendLi.click();
        // 已知缺陷：同用例1，accept 掉"参数类型错误：sessionId"弹窗
        waitForAlert().accept();
        new WebDriverWait(driver, Duration.ofSeconds(5))
                .until(d -> sessionLisByName(userB).stream()
                        .anyMatch(li -> li.getAttribute("message-session-id") != null));

        // 第二次点击同一好友
        driver.findElement(By.cssSelector(".tab .tab-friend")).click();
        driver.findElements(By.cssSelector("#friend-list li")).stream()
                .filter(li -> li.getText().equals(userB))
                .findFirst().get().click();

        // 断言会话列表里 B 的会话只有 1 个
        Assert.assertEquals("重复点击好友不应重复创建会话",
                1, sessionLisByName(userB).size());
    }
}
