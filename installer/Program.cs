using System.Reflection;
using System.Runtime.InteropServices;
using System.Text.Json;
using Microsoft.Web.WebView2.Core;
using Microsoft.Web.WebView2.WinForms;
using Microsoft.Win32;

namespace PowerPlusInstaller;

static class Program
{
    [STAThread]
    static void Main()
    {
        ApplicationConfiguration.Initialize();
        Application.Run(new MainForm());
    }
}

public class MainForm : Form
{
    const string GUID = "629c04eb-661e-43a4-abc4-21a298eb92db";
    const string WEF_KEY = @"Software\Microsoft\Office\16.0\WEF\Developer";

    readonly WebView2 _web = new();
    string _installPath = Path.Combine(
        Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "powerPlus");

    [DllImport("user32.dll")] static extern bool ReleaseCapture();
    [DllImport("user32.dll")] static extern IntPtr SendMessage(IntPtr h, int msg, int wp, int lp);
    [DllImport("dwmapi.dll")] static extern int DwmSetWindowAttribute(IntPtr hwnd, int attr, ref int val, int size);
    [DllImport("gdi32.dll")] static extern IntPtr CreateRoundRectRgn(int x1, int y1, int x2, int y2, int w, int h);

    const int CS_DROPSHADOW = 0x20000;
    protected override CreateParams CreateParams
    {
        get { var cp = base.CreateParams; cp.ClassStyle |= CS_DROPSHADOW; return cp; } // 연한 시스템 그림자
    }

    void ApplyRoundedCorners()
    {
        int r = (int)Math.Round(8 * (DeviceDpi / 96.0)); // 8px (DPI 보정)
        if (Environment.OSVersion.Version.Build >= 22000)
        {
            int pref = 2; // DWMWCP_ROUND (Win11, 부드러운 AA 라운드 + 그림자)
            DwmSetWindowAttribute(Handle, 33, ref pref, sizeof(int));
        }
        else
        {
            Region = System.Drawing.Region.FromHrgn(CreateRoundRectRgn(0, 0, Width + 1, Height + 1, r * 2, r * 2)); // Win10 폴백
        }
    }

    public MainForm()
    {
        FormBorderStyle = FormBorderStyle.None;
        StartPosition = FormStartPosition.CenterScreen;
        AutoScaleMode = AutoScaleMode.Dpi;
        ClientSize = new Size(720, 512);
        BackColor = Color.White;
        Text = "powerPlus 설치 마법사";
        try { Icon = Icon.ExtractAssociatedIcon(Environment.ProcessPath!); } catch { }

        _web.Dock = DockStyle.Fill;
        Controls.Add(_web);
        Load += async (_, __) => { ApplyRoundedCorners(); await InitAsync(); };
    }

    async Task InitAsync()
    {
        var dataDir = Path.Combine(Path.GetTempPath(), "powerPlus_setup_wv2");
        var env = await CoreWebView2Environment.CreateAsync(null, dataDir);
        await _web.EnsureCoreWebView2Async(env);
        var c = _web.CoreWebView2;
        c.Settings.AreDefaultContextMenusEnabled = false;
        c.Settings.IsZoomControlEnabled = false;
        c.Settings.AreDevToolsEnabled = false;
        c.WebMessageReceived += OnMessage;
        c.NavigationCompleted += (_, __) =>
            Post(new { @event = "path", path = _installPath });
        c.NavigateToString(ReadResource("installer.html"));
    }

    void OnMessage(object? sender, CoreWebView2WebMessageReceivedEventArgs e)
    {
        string raw;
        try { raw = e.TryGetWebMessageAsString(); } catch { return; }
        JsonElement m;
        try { m = JsonDocument.Parse(raw).RootElement; } catch { return; }
        var action = m.TryGetProperty("action", out var a) ? a.GetString() : null;
        switch (action)
        {
            case "drag":
                ReleaseCapture();
                SendMessage(Handle, 0xA1, 0x2, 0); // WM_NCLBUTTONDOWN, HTCAPTION
                break;
            case "close":
                Close();
                break;
            case "browse":
                BrowseFolder();
                break;
            case "install":
                _ = DoInstall(m);
                break;
            case "finish":
                var launch = m.TryGetProperty("launch", out var l) && l.ValueKind == JsonValueKind.True;
                if (launch) TryLaunchPowerPoint();
                Close();
                break;
        }
    }

    void BrowseFolder()
    {
        using var dlg = new FolderBrowserDialog { Description = "설치 위치 선택", UseDescriptionForTitle = true };
        try { dlg.SelectedPath = _installPath; } catch { }
        if (dlg.ShowDialog(this) == DialogResult.OK && !string.IsNullOrWhiteSpace(dlg.SelectedPath))
        {
            // 선택 폴더 아래 powerPlus 하위 폴더로 설치
            _installPath = dlg.SelectedPath.TrimEnd('\\').EndsWith("powerPlus", StringComparison.OrdinalIgnoreCase)
                ? dlg.SelectedPath
                : Path.Combine(dlg.SelectedPath, "powerPlus");
            Post(new { @event = "path", path = _installPath });
        }
    }

    async Task DoInstall(JsonElement m)
    {
        try
        {
            await Task.Run(() =>
            {
                Directory.CreateDirectory(_installPath);
                var manifestPath = Path.Combine(_installPath, "manifest.xml");
                File.WriteAllText(manifestPath, ReadResource("manifest.xml"), new System.Text.UTF8Encoding(false));
                // PowerPoint 웹 애드인 사이드로드 등록 (HKCU, 관리자 권한 불필요)
                using var key = Registry.CurrentUser.CreateSubKey(WEF_KEY);
                key.SetValue(GUID, manifestPath, RegistryValueKind.String);
            });
            await Task.Delay(900); // 진행 표시가 자연스럽도록 약간의 텀
            Post(new { @event = "done" });
        }
        catch (Exception ex)
        {
            Post(new { @event = "error", msg = ex.Message });
        }
    }

    void TryLaunchPowerPoint()
    {
        try
        {
            System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo("powerpnt.exe") { UseShellExecute = true });
        }
        catch { /* PowerPoint 미설치 등 — 무시 */ }
    }

    void Post(object o) => _web.CoreWebView2?.PostWebMessageAsString(JsonSerializer.Serialize(o));

    static string ReadResource(string endsWith)
    {
        var asm = Assembly.GetExecutingAssembly();
        var name = asm.GetManifestResourceNames().First(n => n.EndsWith(endsWith, StringComparison.OrdinalIgnoreCase));
        using var s = asm.GetManifestResourceStream(name)!;
        using var r = new StreamReader(s);
        return r.ReadToEnd();
    }
}
