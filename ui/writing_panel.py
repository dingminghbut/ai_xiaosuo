"""Writing panel for chapter generation."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QTextEdit, QLineEdit,
    QComboBox, QSpinBox, QGroupBox, QProgressBar,
    QCheckBox, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal

from ai_xiaosuo.core.chapter_generator import GenerationParams


class WritingPanel(QWidget):
    """Panel for AI chapter writing."""
    
    # Signals
    generate_requested = pyqtSignal(dict)  # Emit generation params
    verify_requested = pyqtSignal(int)  # Emit chapter ID
    
    def __init__(self):
        """Initialize writing panel."""
        super().__init__()
        
        self._current_project_id = None
        self._current_chapter_id = None
        self._current_content = ""
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        
        # Left panel - settings
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Chapter info group
        info_group = QGroupBox("章节信息")
        info_layout = QGridLayout()
        
        info_layout.addWidget(QLabel("章节标题:"), 0, 0)
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("自动生成或手动输入")
        info_layout.addWidget(self.title_edit, 0, 1)
        
        info_layout.addWidget(QLabel("章节序号:"), 1, 0)
        self.chapter_number_spin = QSpinBox()
        self.chapter_number_spin.setMinimum(1)
        self.chapter_number_spin.setMaximum(9999)
        info_layout.addWidget(self.chapter_number_spin, 1, 1)
        
        info_group.setLayout(info_layout)
        left_layout.addWidget(info_group)
        
        # Generation params group
        params_group = QGroupBox("生成参数")
        params_layout = QGridLayout()
        
        params_layout.addWidget(QLabel("本章目标:"), 0, 0, 1, 2)
        self.goal_edit = QTextEdit()
        self.goal_edit.setMaximumHeight(80)
        self.goal_edit.setPlaceholderText("描述本章要达成的目标...")
        params_layout.addWidget(self.goal_edit, 1, 0, 1, 2)
        
        params_layout.addWidget(QLabel("情绪基调:"), 2, 0)
        self.tone_combo = QComboBox()
        self.tone_combo.addItems(["中性", "紧张", "轻松", "悲伤", "热血", "温馨"])
        params_layout.addWidget(self.tone_combo, 2, 1)
        
        params_layout.addWidget(QLabel("结尾钩子:"), 3, 0)
        self.hook_edit = QLineEdit()
        self.hook_edit.setPlaceholderText("设置悬念结尾...")
        params_layout.addWidget(self.hook_edit, 3, 1)
        
        params_layout.addWidget(QLabel("目标字数:"), 4, 0)
        self.word_count_spin = QSpinBox()
        self.word_count_spin.setMinimum(1000)
        self.word_count_spin.setMaximum(10000)
        self.word_count_spin.setSingleStep(500)
        self.word_count_spin.setValue(3000)
        params_layout.addWidget(self.word_count_spin, 4, 1)
        
        params_layout.addWidget(QLabel("对话比例:"), 5, 0)
        self.dialogue_spin = QSpinBox()
        self.dialogue_spin.setMinimum(0)
        self.dialogue_spin.setMaximum(100)
        self.dialogue_spin.setValue(30)
        params_layout.addWidget(self.dialogue_spin, 5, 1)
        
        params_layout.addWidget(QLabel("节奏:"), 6, 0)
        self.pace_combo = QComboBox()
        self.pace_combo.addItems(["慢节奏", "正常", "快节奏"])
        self.pace_combo.setCurrentIndex(1)
        params_layout.addWidget(self.pace_combo, 6, 1)
        
        params_group.setLayout(params_layout)
        left_layout.addWidget(params_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.generate_btn = QPushButton("生成章节")
        self.generate_btn.clicked.connect(self._on_generate)
        self.generate_btn.setMinimumHeight(40)
        btn_layout.addWidget(self.generate_btn)
        
        self.regenerate_btn = QPushButton("重新生成")
        self.regenerate_btn.clicked.connect(self._on_regenerate)
        self.regenerate_btn.setEnabled(False)
        btn_layout.addWidget(self.regenerate_btn)
        
        left_layout.addLayout(btn_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        left_layout.addWidget(self.progress_bar)
        
        # Verify button
        self.verify_btn = QPushButton("确认章节")
        self.verify_btn.clicked.connect(self._on_verify)
        self.verify_btn.setEnabled(False)
        self.verify_btn.setMinimumHeight(40)
        left_layout.addWidget(self.verify_btn)
        
        left_layout.addStretch()
        
        # Right panel - content display
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        right_layout.addWidget(QLabel("章节内容:"))
        
        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        self.content_edit = QTextEdit()
        self.content_edit.setReadOnly(False)
        self.content_edit.setPlaceholderText("生成的内容将显示在这里...")
        
        scroll.setWidget(self.content_edit)
        right_layout.addWidget(scroll)
        
        # Title suggestions
        titles_group = QGroupBox("候选标题")
        titles_layout = QVBoxLayout()
        
        self.titles_label = QLabel("暂无")
        self.titles_label.setWordWrap(True)
        titles_layout.addWidget(self.titles_label)
        
        titles_group.setLayout(titles_layout)
        right_layout.addWidget(titles_group)
        
        # Split layout
        split_layout = QHBoxLayout()
        split_layout.addWidget(left_widget, 1)
        split_layout.addWidget(right_widget, 2)
        
        layout.addLayout(split_layout)
    
    def _get_generation_params(self) -> dict:
        """Get generation parameters from UI.
        
        Returns:
            Dict of generation parameters
        """
        return {
            "chapter_goal": self.goal_edit.toPlainText(),
            "emotional_tone": self.tone_combo.currentText(),
            "ending_hook": self.hook_edit.text(),
            "special_events": "",
            "target_words": self.word_count_spin.value(),
            "dialogue_ratio": self.dialogue_spin.value(),
            "pace": ["slow", "normal", "fast"][self.pace_combo.currentIndex()],
            "chapter_number": self.chapter_number_spin.value(),
            "title": self.title_edit.text(),
        }
    
    def _on_generate(self):
        """Handle generate button click."""
        if not self._current_project_id:
            return
        
        params = self._get_generation_params()
        self.generate_requested.emit(params)
    
    def _on_regenerate(self):
        """Handle regenerate button click."""
        self._on_generate()
    
    def _on_verify(self):
        """Handle verify button click."""
        if self._current_chapter_id:
            self.verify_requested.emit(self._current_chapter_id)
    
    # Public methods
    def set_project(self, project_id: int):
        """Set current project.
        
        Args:
            project_id: Project ID
        """
        self._current_project_id = project_id
        self.generate_btn.setEnabled(True)
    
    def set_chapter_number(self, number: int):
        """Set chapter number.
        
        Args:
            number: Chapter number
        """
        self.chapter_number_spin.setValue(number)
    
    def display_generation(self, content: str, titles: list[str]):
        """Display generated content.
        
        Args:
            content: Generated content
            titles: Title candidates
        """
        self.content_edit.setPlainText(content)
        self._current_content = content
        
        # Display titles
        if titles:
            titles_text = "\n".join([f"• {t}" for t in titles[:8]])
            self.titles_label.setText(titles_text)
        
        self.regenerate_btn.setEnabled(True)
        self.verify_btn.setEnabled(True)
    
    def display_error(self, error: str):
        """Display error message.
        
        Args:
            error: Error message
        """
        self.content_edit.setPlainText(f"生成失败: {error}")
    
    def set_progress(self, progress: int):
        """Set progress bar value.
        
        Args:
            progress: Progress percentage (0-100)
        """
        if progress < 0 or progress > 100:
            self.progress_bar.setVisible(False)
        else:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(progress)
    
    def set_chapter_id(self, chapter_id: int):
        """Set current chapter ID.
        
        Args:
            chapter_id: Chapter ID
        """
        self._current_chapter_id = chapter_id
    
    def get_content(self) -> str:
        """Get current content.
        
        Returns:
            Current chapter content
        """
        return self.content_edit.toPlainText()
    
    def get_title(self) -> str:
        """Get current title.
        
        Returns:
            Current title
        """
        return self.title_edit.text()
