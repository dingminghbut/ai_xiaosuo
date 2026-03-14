"""Main window for AI Xiaosuo application."""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QMenuBar, QMenu, QStatusBar, QToolBar,
    QMessageBox, QLabel, QPushButton
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QIcon

from ai_xiaosuo.config import WINDOW_WIDTH, WINDOW_HEIGHT


class MainWindow(QMainWindow):
    """Main window for AI Xiaosuo writing assistant."""
    
    def __init__(self):
        """Initialize main window."""
        super().__init__()
        
        self.setWindowTitle("AI番茄写作助手")
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Center window
        self._center_window()
        
        # Initialize UI
        self._init_ui()
        
        # Status bar timer
        self._status_timer = QTimer()
        self._status_timer.timeout.connect(self._update_status)
        self._status_timer.start(1000)  # Update every second
        
        self._current_project_id = None
        self._current_chapter_id = None
    
    def _center_window(self):
        """Center the window on screen."""
        screen = self.screen()
        if screen:
            geometry = screen.availableGeometry()
            x = (geometry.width() - self.width()) // 2
            y = (geometry.height() - self.height()) // 2
            self.move(x, y)
    
    def _init_ui(self):
        """Initialize UI components."""
        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Create main layout
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        
        # Create menu bar
        self._create_menu_bar()
        
        # Create toolbar
        self._create_toolbar()
        
        # Create status bar
        self._create_status_bar()
    
    def _create_menu_bar(self):
        """Create menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("文件(&F)")
        
        new_project_action = QAction("新建项目(&N)", self)
        new_project_action.setShortcut("Ctrl+N")
        new_project_action.triggered.connect(self._on_new_project)
        file_menu.addAction(new_project_action)
        
        open_project_action = QAction("打开项目(&O)", self)
        open_project_action.setShortcut("Ctrl+O")
        open_project_action.triggered.connect(self._on_open_project)
        file_menu.addAction(open_project_action)
        
        file_menu.addSeparator()
        
        save_action = QAction("保存(&S)", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._on_save)
        file_menu.addAction(save_action)
        
        export_action = QAction("导出(&E)", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self._on_export)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("编辑(&E)")
        
        undo_action = QAction("撤销(&U)", self)
        undo_action.setShortcut("Ctrl+Z")
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("重做(&R)", self)
        redo_action.setShortcut("Ctrl+Y")
        edit_menu.addAction(redo_action)
        
        # View menu
        view_menu = menubar.addMenu("视图(&V)")
        
        # Project menu
        project_menu = menubar.addMenu("项目(&P)")
        
        generate_chapter_action = QAction("生成章节(&G)", self)
        generate_chapter_action.setShortcut("Ctrl+G")
        generate_chapter_action.triggered.connect(self._on_generate_chapter)
        project_menu.addAction(generate_chapter_action)
        
        verify_chapter_action = QAction("确认章节(&V)", self)
        verify_chapter_action.setShortcut("Ctrl+Enter")
        verify_chapter_action.triggered.connect(self._on_verify_chapter)
        project_menu.addAction(verify_chapter_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("工具(&T)")
        
        check_action = QAction("内容检查(&C)", self)
        check_action.setShortcut("F5")
        check_action.triggered.connect(self._on_check_content)
        tools_menu.addAction(check_action)
        
        # Help menu
        help_menu = menubar.addMenu("帮助(&H)")
        
        about_action = QAction("关于(&A)", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)
    
    def _create_toolbar(self):
        """Create toolbar."""
        toolbar = QToolBar("主工具栏")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # New project button
        new_btn = QPushButton("新建项目")
        new_btn.clicked.connect(self._on_new_project)
        toolbar.addWidget(new_btn)
        
        toolbar.addSeparator()
        
        # Generate chapter button
        self.generate_btn = QPushButton("生成章节")
        self.generate_btn.clicked.connect(self._on_generate_chapter)
        self.generate_btn.setEnabled(False)
        toolbar.addWidget(self.generate_btn)
        
        # Verify button
        self.verify_btn = QPushButton("确认章节")
        self.verify_btn.clicked.connect(self._on_verify_chapter)
        self.verify_btn.setEnabled(False)
        toolbar.addWidget(self.verify_btn)
        
        toolbar.addSeparator()
        
        # Check button
        check_btn = QPushButton("内容检查")
        check_btn.clicked.connect(self._on_check_content)
        toolbar.addWidget(check_btn)
        
        # Cost display
        self.cost_label = QLabel("今日消耗: $0.00")
        toolbar.addWidget(self.cost_label)
    
    def _create_status_bar(self):
        """Create status bar."""
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        # Status labels
        self.status_label = QLabel("就绪")
        self.statusBar.addWidget(self.status_label, 1)
        
        self.project_label = QLabel("未选择项目")
        self.statusBar.addWidget(self.project_label)
        
        self.chapter_label = QLabel("")
        self.statusBar.addWidget(self.chapter_label)
    
    def _update_status(self):
        """Update status bar."""
        # This can be overridden to show dynamic status
        pass
    
    # Menu action handlers
    def _on_new_project(self):
        """Handle new project action."""
        pass
    
    def _on_open_project(self):
        """Handle open project action."""
        pass
    
    def _on_save(self):
        """Handle save action."""
        pass
    
    def _on_export(self):
        """Handle export action."""
        pass
    
    def _on_generate_chapter(self):
        """Handle generate chapter action."""
        pass
    
    def _on_verify_chapter(self):
        """Handle verify chapter action."""
        pass
    
    def _on_check_content(self):
        """Handle check content action."""
        pass
    
    def _on_about(self):
        """Handle about action."""
        QMessageBox.about(
            self,
            "关于 AI番茄写作助手",
            "AI番茄写作助手 v1.0\n\n"
            "基于MiniMax M2.5的AI写作助手\n"
            "支持自动写作、自动检查、记忆更新等功能\n\n"
            "适用于番茄小说平台的长篇连载创作"
        )
    
    # Public methods for panel communication
    def set_current_project(self, project_id: int, project_name: str):
        """Set current project.
        
        Args:
            project_id: Project ID
            project_name: Project name
        """
        self._current_project_id = project_id
        self.project_label.setText(f"项目: {project_name}")
        self.generate_btn.setEnabled(True)
    
    def set_current_chapter(self, chapter_id: int, chapter_num: int):
        """Set current chapter.
        
        Args:
            chapter_id: Chapter ID
            chapter_num: Chapter number
        """
        self._current_chapter_id = chapter_id
        self.chapter_label.setText(f"章节: 第{chapter_num}章")
        self.verify_btn.setEnabled(True)
    
    def update_cost(self, cost: float):
        """Update cost display.
        
        Args:
            cost: Current cost in USD
        """
        self.cost_label.setText(f"今日消耗: ${cost:.2f}")
    
    def show_status(self, message: str):
        """Show status message.
        
        Args:
            message: Status message
        """
        self.status_label.setText(message)
    
    def add_tab(self, widget, title: str) -> int:
        """Add a tab to the tab widget.
        
        Args:
            widget: Widget to add
            title: Tab title
            
        Returns:
            Tab index
        """
        return self.tab_widget.addTab(widget, title)
    
    def remove_tab(self, index: int):
        """Remove a tab from the tab widget.
        
        Args:
            index: Tab index
        """
        self.tab_widget.removeTab(index)
    
    def set_tab_enabled(self, index: int, enabled: bool):
        """Enable or disable a tab.
        
        Args:
            index: Tab index
            enabled: Whether to enable
        """
        self.tab_widget.setTabEnabled(index, enabled)
