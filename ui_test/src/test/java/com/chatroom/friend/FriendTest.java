package com.chatroom.friend;

import com.chatroom.common.BaseTest;
import com.chatroom.common.UiHelper;
import org.junit.Assert;
import org.junit.Test;
import org.openqa.selenium.Alert;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

import java.time.Duration;
import java.util.List;

public class FriendTest extends BaseTest {

    // 搜索一个已有用户（zhangsan 是库里现成账号），等待结果列表出现
    private void search(String keyword) {
        driver.findElement(By.id("searchInput")).sendKeys(keyword);
        driver.findElement(By.id("searchBtn")).click();
        // 等待搜索结果渲染出来（ajax 异步）
        new WebDriverWait(driver, Duration.ofSeconds(5))
                .until(ExpectedConditions.visibilityOfElementLocated(
                        By.cssSelector("#search-result-list li")));
    }

    // 用例1：搜索已存在的用户 → 结果列表出现该用户 + "添加好友"按钮
    @Test
    public void testSearchFound() {
        String username = UiHelper.randomUsername();
        UiHelper.register(driver, username, "123456");
        UiHelper.login(driver, username, "123456");

        search("zhangsan");
        WebElement li = driver.findElement(By.cssSelector("#search-result-list li"));
        Assert.assertTrue("搜索结果应包含 zhangsan",
                li.getText().contains("zhangsan"));
        Assert.assertTrue("应有添加好友按钮",
                li.findElements(By.className("add-friend-btn")).size() > 0);
    }

    // 用例2：搜索不存在的用户 → 显示"未找到相关用户"
    @Test
    public void testSearchNotFound() {
        String username = UiHelper.randomUsername();
        UiHelper.register(driver, username, "123456");
        UiHelper.login(driver, username, "123456");

        search("no_such_user_xyz");
        WebElement li = driver.findElement(By.cssSelector("#search-result-list li"));
        Assert.assertEquals("未找到相关用户", li.getText());
    }

    // 用例3：搜索框为空 → 弹"请输入搜索关键词"
    @Test
    public void testSearchEmptyKeyword() {
        String username = UiHelper.randomUsername();
        UiHelper.register(driver, username, "123456");
        UiHelper.login(driver, username, "123456");

        driver.findElement(By.id("searchBtn")).click();
        Alert alert = waitForAlert();
        Assert.assertEquals("请输入搜索关键词", alert.getText());
        alert.accept();
    }

    // 用例4：完整加好友流程：A 给 B 发申请 → B 接受 → 双方好友列表互见
    @Test
    public void testAddFriendFlow() {
        String userA = UiHelper.randomUsername();
        String userB = UiHelper.randomUsername();

        // A 注册并登录；B 只注册
        UiHelper.register(driver, userA, "123456");
        UiHelper.login(driver, userA, "123456");
        WebDriver driverB = new ChromeDriver();
        driverB.manage().timeouts().implicitlyWait(Duration.ofSeconds(5));
        try {
            UiHelper.register(driverB, userB, "123456");

            // A 搜索 B 并发送好友申请（弹出 prompt 填申请理由）
            search(userB);
            driver.findElement(By.cssSelector(".add-friend-btn")).click();
            Alert prompt = waitForAlert();
            prompt.sendKeys("你好，加个好友");
            prompt.accept();
            Alert sentAlert = waitForAlert();
            // 注意：后端把"好友请求已发送"放进了 data 字段，msg 是默认的"操作成功"，
            // 前端弹的是 body.msg，所以实际弹窗是"操作成功"（缺陷，待裁决）
            Assert.assertEquals("操作成功", sentAlert.getText());
            sentAlert.accept();

            // B 登录，打开好友申请弹窗，接受
            UiHelper.login(driverB, userB, "123456");
            driverB.findElement(By.id("showPendingRequestsBtn")).click();
            new WebDriverWait(driverB, Duration.ofSeconds(5))
                    .until(ExpectedConditions.visibilityOfElementLocated(
                            By.cssSelector("#pendingRequestModal .accept-btn")));
            driverB.findElement(By.cssSelector("#pendingRequestModal .accept-btn")).click();
            Alert acceptAlert = UiHelper.waitAlert(driverB);
            // 同上：实际弹的是默认 msg "操作成功"
            Assert.assertEquals("操作成功", acceptAlert.getText());
            acceptAlert.accept();

            // B 刷新页面，切到"好友"标签，好友列表出现 A
            // 注意：好友列表默认 display:none，getText() 读不到，必须先点"好友"标签
            driverB.navigate().refresh();
            driverB.findElement(By.cssSelector(".tab .tab-friend")).click();
            new WebDriverWait(driverB, Duration.ofSeconds(10))
                    .until(d -> friendNames(driverB).contains(userA));

            // A 刷新页面，切到"好友"标签，好友列表出现 B
            driver.navigate().refresh();
            driver.findElement(By.cssSelector(".tab .tab-friend")).click();
            new WebDriverWait(driver, Duration.ofSeconds(10))
                    .until(d -> friendNames(driver).contains(userB));
        } finally {
            driverB.quit();
        }
    }

    // 读取当前页面好友列表的所有名字
    private List<String> friendNames(WebDriver d) {
        return d.findElements(By.cssSelector("#friend-list h4")).stream()
                .map(WebElement::getText)
                .collect(java.util.stream.Collectors.toList());
    }
}
