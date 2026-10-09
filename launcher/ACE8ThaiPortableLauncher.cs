using System;
using System.Diagnostics;
using System.IO;
using System.Threading;
using System.Windows.Forms;
class ACE8ThaiPortableLauncher {
  static readonly string Root = AppDomain.CurrentDomain.BaseDirectory;
  static readonly string Log = Path.Combine(Root,"ACE8Thai_Launcher.log");
  static void Record(string text) { File.AppendAllText(Log,DateTimeOffset.Now.ToString("o")+" "+text+Environment.NewLine); }
  [STAThread] static int Main(string[] args) {
    try {
      var info=new ProcessStartInfo(Path.Combine(Root,"start_protected_game.exe"),"-SaveToUserDir -anticheat_settings=ACE8Thai_Offline.json");
      info.WorkingDirectory=Root;info.UseShellExecute=false;
      info.EnvironmentVariables["EOS_USE_ANTICHEATCLIENTNULL"]="1";
      info.EnvironmentVariables["SteamAppId"]="2288340";
      info.EnvironmentVariables["SteamGameId"]="2288340";
      if(!File.Exists(info.FileName)||!File.Exists(Path.Combine(Root,"EasyAntiCheat","ACE8Thai_Offline.json")))
        throw new Exception("กรุณาวางไฟล์ม็อดในโฟลเดอร์เกมที่มี start_protected_game.exe แล้วเปิด Steam ค้างไว้");
      if(Array.IndexOf(args,"--self-test")>=0) {
        if(info.UseShellExecute||info.EnvironmentVariables["EOS_USE_ANTICHEATCLIENTNULL"]!="1")throw new Exception("Launcher self-test failed");
        Record("SELF-TEST PASSED; root="+Root+"; no game started");return 0;
      }
      if(Process.GetProcessesByName("AceCombat8").Length>0||Process.GetProcessesByName("start_protected_game").Length>0) { Record("Game already running");return 0; }
      if(Process.GetProcessesByName("steam").Length==0)throw new Exception("กรุณาเปิด Steam และเข้าสู่บัญชีที่มีเกมก่อน");
      Record("OFFLINE LAUNCH; null client=1; settings=ACE8Thai_Offline.json");
      using(var bootstrap=Process.Start(info)) { bootstrap.WaitForExit();Record("Bootstrap exit="+bootstrap.ExitCode);if(bootstrap.ExitCode!=0)return bootstrap.ExitCode; }
      Process game=null;
      for(int i=0;i<100;i++){var games=Process.GetProcessesByName("AceCombat8");if(games.Length>0){game=games[0];break;}Thread.Sleep(200);}
      if(game!=null){using(game){Record("Game process detected; PID="+game.Id);game.WaitForExit();Record("Game session ended");}}
      else Record("No game process detected; inspect game error");
      return 0;
    } catch(Exception ex){try{Record("ERROR "+ex.Message);}catch{}MessageBox.Show(ex.Message,"ACE8 Thai — หน๊ด หนวด translator");return 1;}
  }
}
