using System;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.IO;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace THub.ACE8 {
    static class SetupBranding {
        [DllImport("shell32.dll",CharSet=CharSet.Unicode)]
        static extern int SetCurrentProcessExplicitAppUserModelID(string appId);
        public static void Initialize(){SetCurrentProcessExplicitAppUserModelID("NodNuatTranslator.ACE8.ThaiSetup");}
    }
    sealed class Artwork : Control {
        readonly Image image;
        public Artwork() {
            DoubleBuffered=true;
            using(var input=Assembly.GetExecutingAssembly().GetManifestResourceStream("THub.ACE8.Header"))
            using(var source=Image.FromStream(input)) image=new Bitmap(source);
        }
        protected override void OnResize(EventArgs e){base.OnResize(e);Height=(int)Math.Round(Width*630.0/1702.0);}
        protected override void OnPaint(PaintEventArgs e){e.Graphics.InterpolationMode=InterpolationMode.HighQualityBicubic;e.Graphics.DrawImage(image,ClientRectangle);}
        protected override void Dispose(bool disposing){if(disposing)image.Dispose();base.Dispose(disposing);}
    }
    static class Theme {
        public static readonly Color Background=Color.FromArgb(16,21,27),Card=Color.FromArgb(25,33,42),
            Border=Color.FromArgb(48,60,72),Text=Color.FromArgb(243,243,236),Muted=Color.FromArgb(166,179,190),
            Blue=Color.FromArgb(46,150,195),Gold=Color.FromArgb(219,197,139);
        public static GraphicsPath Round(Rectangle r,int radius){
            var p=new GraphicsPath();int d=radius*2;
            p.AddArc(r.X,r.Y,d,d,180,90);p.AddArc(r.Right-d,r.Y,d,d,270,90);
            p.AddArc(r.Right-d,r.Bottom-d,d,d,0,90);p.AddArc(r.X,r.Bottom-d,d,d,90,90);p.CloseFigure();return p;
        }
    }
    sealed class CardPanel : Panel {
        public Color Fill=Theme.Card,Line=Theme.Border;
        public CardPanel(){DoubleBuffered=true;BackColor=Theme.Background;}
        protected override void OnPaint(PaintEventArgs e){
            e.Graphics.SmoothingMode=SmoothingMode.AntiAlias;
            using(var path=Theme.Round(new Rectangle(0,0,Width-1,Height-1),12))
            using(var fill=new SolidBrush(Fill))using(var pen=new Pen(Line)){
                e.Graphics.FillPath(fill,path);e.Graphics.DrawPath(pen,path);
            }
            base.OnPaint(e);
        }
    }
    sealed class ActionButton : Button {
        public bool Primary;
        bool hover;
        public ActionButton(){FlatStyle=FlatStyle.Flat;FlatAppearance.BorderSize=0;DoubleBuffered=true;Cursor=Cursors.Hand;UseVisualStyleBackColor=false;BackColor=Theme.Background;}
        protected override void OnMouseEnter(EventArgs e){hover=true;Invalidate();base.OnMouseEnter(e);}
        protected override void OnMouseLeave(EventArgs e){hover=false;Invalidate();base.OnMouseLeave(e);}
        protected override void OnPaint(PaintEventArgs e){
            e.Graphics.SmoothingMode=SmoothingMode.AntiAlias;
            var fill=Primary?(hover?Color.FromArgb(61,170,212):Theme.Blue):(hover?Color.FromArgb(39,52,65):Theme.Card);
            if(!Enabled)fill=Theme.Border;
            using(var path=Theme.Round(new Rectangle(0,0,Width-1,Height-1),9))
            using(var brush=new SolidBrush(fill))using(var pen=new Pen(Primary?fill:Theme.Border)){
                e.Graphics.FillPath(brush,path);e.Graphics.DrawPath(pen,path);
            }
            TextRenderer.DrawText(e.Graphics,Text,Font,ClientRectangle,Enabled?Theme.Text:Theme.Muted,TextFormatFlags.HorizontalCenter|TextFormatFlags.VerticalCenter);
            if(Focused&&ShowFocusCues)ControlPaint.DrawFocusRectangle(e.Graphics,new Rectangle(5,5,Width-10,Height-10),Theme.Text,fill);
        }
    }
    public sealed class OfflineWindow : Form {
        readonly TextBox path=new TextBox();readonly Label status=new Label();
        readonly ActionButton install=new ActionButton(),uninstall=new ActionButton(),browse=new ActionButton();
        readonly ProgressBar progress=new ProgressBar();bool busy;
        static Label Label(string text,float size,Color color,bool bold=false){
            return new Label {Text=text,Font=new Font("Leelawadee UI",size,bold?FontStyle.Bold:FontStyle.Regular),ForeColor=color,BackColor=Color.Transparent,AutoSize=false};
        }
        public OfflineWindow(){
            SetupBranding.Initialize();
            using(var stream=Assembly.GetExecutingAssembly().GetManifestResourceStream("THub.ACE8.ProgramIcon"))
            using(var source=new Icon(stream))Icon=(Icon)source.Clone();
            ShowIcon=true;ShowInTaskbar=true;
            Text="NodNuat Translator  |  ACE COMBAT 8 — ม็อดภาษาไทย 2.4";
            BackColor=Theme.Background;ForeColor=Theme.Text;Font=new Font("Leelawadee UI",10);
            AutoScaleDimensions=new SizeF(96,96);AutoScaleMode=AutoScaleMode.Dpi;ClientSize=new Size(960,900);MinimumSize=new Size(740,620);
            StartPosition=FormStartPosition.CenterScreen;
            var scroll=new Panel {Dock=DockStyle.Fill,AutoScroll=true,BackColor=Theme.Background};Controls.Add(scroll);
            var page=new TableLayoutPanel {Dock=DockStyle.Top,AutoSize=true,ColumnCount=1,Margin=Padding.Empty,Padding=Padding.Empty,BackColor=Theme.Background};
            page.ColumnStyles.Add(new ColumnStyle(SizeType.Percent,100));scroll.Controls.Add(page);
            var art=new Artwork {Dock=DockStyle.Fill,Margin=Padding.Empty,Height=355};page.Controls.Add(art);
            var accent=new Panel {Height=3,Dock=DockStyle.Fill,BackColor=Theme.Blue,Margin=Padding.Empty};page.Controls.Add(accent);
            var body=new TableLayoutPanel {Dock=DockStyle.Fill,AutoSize=true,ColumnCount=1,Padding=new Padding(28,20,28,14),Margin=Padding.Empty,BackColor=Theme.Background};
            body.ColumnStyles.Add(new ColumnStyle(SizeType.Percent,100));page.Controls.Add(body);
            var heading=new Panel {Dock=DockStyle.Fill,Height=66,Margin=Padding.Empty};body.Controls.Add(heading);
            var title=Label("ติดตั้งม็อดภาษาไทย",21,Theme.Text,true);title.SetBounds(0,0,600,39);heading.Controls.Add(title);
            var sub=Label("STEAM  ·  BUILD 25201480  ·  CAMPAIGN",9,Theme.Muted);sub.SetBounds(2,43,650,20);heading.Controls.Add(sub);
            var version=Label("2.4",9,Theme.Gold,true);version.TextAlign=ContentAlignment.MiddleRight;
            version.SetBounds(heading.Width-170,3,166,32);version.Anchor=AnchorStyles.Top|AnchorStyles.Right;heading.Controls.Add(version);
            var folder=new CardPanel {Dock=DockStyle.Fill,Height=103,Margin=new Padding(0,12,0,0)};body.Controls.Add(folder);
            var folderTitle=Label("ตำแหน่งเกม",10,Theme.Muted,true);folderTitle.SetBounds(17,12,300,25);folder.Controls.Add(folderTitle);
            var entry=new Panel {BackColor=Color.FromArgb(14,21,28)};entry.SetBounds(17,46,folder.Width-136,38);entry.Anchor=AnchorStyles.Top|AnchorStyles.Left|AnchorStyles.Right;folder.Controls.Add(entry);
            path.AccessibleName="ตำแหน่งเกม";path.BorderStyle=BorderStyle.None;path.BackColor=entry.BackColor;path.ForeColor=Theme.Text;path.Font=new Font("Segoe UI",10);path.SetBounds(10,9,entry.Width-20,23);path.Anchor=AnchorStyles.Left|AnchorStyles.Top|AnchorStyles.Right;entry.Controls.Add(path);
            browse.Text="เปลี่ยน";browse.Font=new Font("Leelawadee UI",10);browse.SetBounds(folder.Width-107,46,90,38);browse.Anchor=AnchorStyles.Top|AnchorStyles.Right;folder.Controls.Add(browse);
            browse.Click+=delegate {using(var d=new FolderBrowserDialog {Description="เลือกโฟลเดอร์หลัก ACE COMBAT 8 ที่มี start_protected_game.exe",ShowNewFolderButton=false})if(d.ShowDialog(this)==DialogResult.OK)path.Text=d.SelectedPath;};
            var caution=new CardPanel {Dock=DockStyle.Fill,Height=93,Margin=new Padding(0,12,0,0),Fill=Color.FromArgb(39,36,28),Line=Color.FromArgb(85,74,47)};body.Controls.Add(caution);
            var mark=Label("!",19,Theme.Gold,true);mark.TextAlign=ContentAlignment.MiddleCenter;mark.SetBounds(12,14,30,36);caution.Controls.Add(mark);
            var warningTitle=Label("ใช้เฉพาะโหมดเนื้อเรื่อง (Campaign)",10.5f,Theme.Gold,true);warningTitle.SetBounds(51,11,caution.Width-68,26);warningTitle.Anchor=AnchorStyles.Left|AnchorStyles.Right|AnchorStyles.Top;caution.Controls.Add(warningTitle);
            var warning=Label("ปิดเกมก่อนติดตั้ง • เปิดเกมผ่าน ACE8ThaiLauncher\nใช้ตัวเปิด Offline ของม็อด — ถอนก่อนเล่นออนไลน์",9.5f,Color.FromArgb(205,196,175));
            warning.SetBounds(51,39,caution.Width-68,46);warning.Anchor=AnchorStyles.Left|AnchorStyles.Right|AnchorStyles.Top;caution.Controls.Add(warning);
            var actions=new TableLayoutPanel {Dock=DockStyle.Fill,Height=54,ColumnCount=2,Margin=new Padding(0,18,0,0)};
            actions.ColumnStyles.Add(new ColumnStyle(SizeType.Percent,65));actions.ColumnStyles.Add(new ColumnStyle(SizeType.Percent,35));body.Controls.Add(actions);
            install.Text="ติดตั้งภาษาไทย 2.4";install.Primary=true;install.Font=new Font("Leelawadee UI",12,FontStyle.Bold);install.Dock=DockStyle.Fill;install.Margin=new Padding(0,0,12,0);actions.Controls.Add(install);
            uninstall.Text="ถอนม็อด";uninstall.Font=new Font("Leelawadee UI",11);uninstall.Dock=DockStyle.Fill;uninstall.Margin=Padding.Empty;actions.Controls.Add(uninstall);
            install.Click+=async delegate {await Run(true);};uninstall.Click+=async delegate {await Run(false);};
            var connection=Label("ติดตั้ง 18 ไฟล์ • สำรองอัตโนมัติ • พื้นที่ว่างประมาณ 144 MB",9,Theme.Muted);
            connection.Dock=DockStyle.Fill;connection.Height=26;connection.Margin=new Padding(1,8,0,0);body.Controls.Add(connection);
            progress.Style=ProgressBarStyle.Marquee;progress.MarqueeAnimationSpeed=22;progress.Dock=DockStyle.Fill;progress.Height=3;progress.Margin=new Padding(0,6,0,0);progress.Visible=false;body.Controls.Add(progress);
            status.Text="กำลังค้นหาเกมอัตโนมัติ…";status.ForeColor=Color.FromArgb(150,206,193);status.Font=new Font("Leelawadee UI",9.5f);status.Dock=DockStyle.Fill;status.Height=53;status.Margin=new Padding(1,9,0,0);body.Controls.Add(status);
            var footer=new Panel {Dock=DockStyle.Fill,Height=30,Margin=new Padding(0,7,0,0)};body.Controls.Add(footer);
            var credit=Label("AI แปล · เกลาคำและ QA ด้วย THub Studio 2.2",8.5f,Theme.Muted);credit.SetBounds(0,3,550,23);footer.Controls.Add(credit);
            var brand=Label("NODNUAT TRANSLATOR",8,Theme.Gold,true);brand.TextAlign=ContentAlignment.MiddleRight;brand.SetBounds(footer.Width-220,2,216,24);brand.Anchor=AnchorStyles.Top|AnchorStyles.Right;footer.Controls.Add(brand);
            AutoGamePath.Bind(this,path,status);
            FormClosing+=delegate(object sender,FormClosingEventArgs e){if(busy){e.Cancel=true;status.Text="กำลังบันทึกไฟล์ กรุณารอให้งานเสร็จก่อนปิดหน้าต่าง";}};
        }
        async Task Run(bool installing){
            if(busy)return;busy=true;install.Enabled=uninstall.Enabled=browse.Enabled=path.Enabled=false;progress.Visible=true;
            status.Text=installing?"กำลังสำรองไฟล์และติดตั้งภาษาไทย…":"กำลังถอนเฉพาะไฟล์ม็อด…";
            var root=path.Text;
            try{
                await Task.Run(()=>{if(installing)Engine.Install(root);else Engine.Uninstall(root);AutoGamePath.Remember(root);});
                status.ForeColor=Color.FromArgb(150,206,193);
                status.Text=installing?"ติดตั้งภาษาไทย 2.4 แล้ว — เปิดผ่าน ACE8ThaiLauncher ในโฟลเดอร์เกม\nเปิด Steam ค้างไว้ และถอนม็อดก่อนเล่นออนไลน์":"ถอนเฉพาะไฟล์ม็อดแล้ว — ไฟล์เกมต้นฉบับและเซฟไม่เปลี่ยน";
            }catch(Exception e){status.ForeColor=Theme.Gold;status.Text=e.Message;MessageBox.Show(this,e.Message,"ยังไม่สำเร็จ",MessageBoxButtons.OK,MessageBoxIcon.Information);}
            finally{busy=false;install.Enabled=uninstall.Enabled=browse.Enabled=path.Enabled=true;progress.Visible=false;}
        }
        public void PreparePreview(string root){path.Text=root;status.Text="พบเกมแล้ว — กดติดตั้งได้เลย";}
    }
}
