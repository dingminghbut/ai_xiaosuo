"""Project panel for managing projects and chapters."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QLineEdit, QTextEdit,
    QGroupBox, QScrollArea, QFrame, QListWidget,
    QListWidgetItem, QComboBox, QSpinBox, QDialog,
    QDialogButtonBox, QFormLayout, QTableWidget,
    QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt, pyqtSignal


class ProjectDialog(QDialog):
    """Dialog for creating/editing a project."""
    
    def __init__(self, parent=None, project_data=None):
        """Initialize project dialog.
        
        Args:
            parent: Parent widget
            project_data: Existing project data for editing
        """
        super().__init__(parent)
        
        self.project_data = project_data or {}
        self.setWindowTitle("新建项目" if not project_data else "编辑项目")
        self.setMinimumWidth(500)
        
        self._init_ui()
        
        if project_data:
            self._populate_data()
    
    def _init_ui(self):
        """Initialize UI."""
        layout = QFormLayout(self)
        
        # Project name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("输入项目名称")
        layout.addRow("项目名称:", self.name_edit)
        
        # Description
        self.desc_edit = QTextEdit()
        self.desc_edit.setMaximumHeight(80)
        layout.addRow("项目描述:", self.desc_edit)
        
        # Genre
        self.genre_combo = QComboBox()
        self.genre_combo.addItems(["玄幻", "仙侠", "都市", "历史", "科幻", "游戏", "其他"])
        layout.addRow("小说类型:", self.genre_combo)
        
        # Target platform
        self.platform_combo = QComboBox()
        self.platform_combo.addItems(["番茄小说", "起点中文网", "纵横中文网", "其他"])
        layout.addRow("目标平台:", self.platform_combo)
        
        # World setting
        self.world_edit = QTextEdit()
        self.world_edit.setMaximumHeight(100)
        self.world_edit.setPlaceholderText("世界观设定（可选）...")
        layout.addRow("世界观设定:", self.world_edit)
        
        # Protagonist setting
        self.protagonist_edit = QTextEdit()
        self.protagonist_edit.setMaximumHeight(80)
        self.protagonist_edit.setPlaceholderText("主角设定（可选）...")
        layout.addRow("主角设定:", self.protagonist_edit)
        
        # Style requirement
        self.style_edit = QLineEdit()
        self.style_edit.setPlaceholderText("文风要求，如：轻松搞笑、严肃大气")
        layout.addRow("文风要求:", self.style_edit)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
    
    def _populate_data(self):
        """Populate fields with existing data."""
        self.name_edit.setText(self.project_data.get("name", ""))
        self.desc_edit.setText(self.project_data.get("description", ""))
        
        # Set combo values
        genre = self.project_data.get("genre", "")
        if genre in ["玄幻", "仙侠", "都市", "历史", "科幻", "游戏", "其他"]:
            self.genre_combo.setCurrentText(genre)
        
        platform = self.project_data.get("target_platform", "")
        if platform:
            self.platform_combo.setCurrentText(platform)
        
        self.world_edit.setText(self.project_data.get("world_setting", ""))
        self.protagonist_edit.setText(self.project_data.get("protagonist_setting", ""))
        self.style_edit.setText(self.project_data.get("style_requirement", ""))
    
    def get_data(self) -> dict:
        """Get project data from form.
        
        Returns:
            Dict of project data
        """
        return {
            "name": self.name_edit.text(),
            "description": self.desc_edit.toPlainText(),
            "genre": self.genre_combo.currentText(),
            "target_platform": self.platform_combo.currentText(),
            "world_setting": self.world_edit.toPlainText(),
            "protagonist_setting": self.protagonist_edit.toPlainText(),
            "style_requirement": self.style_edit.text(),
        }


class CharacterDialog(QDialog):
    """Dialog for creating/editing a character."""
    
    def __init__(self, parent=None, character_data=None):
        """Initialize character dialog.
        
        Args:
            parent: Parent widget
            character_data: Existing character data
        """
        super().__init__(parent)
        
        self.character_data = character_data or {}
        self.setWindowTitle("新建人物" if not character_data else "编辑人物")
        self.setMinimumWidth(400)
        
        self._init_ui()
        
        if character_data:
            self._populate_data()
    
    def _init_ui(self):
        """Initialize UI."""
        layout = QFormLayout(self)
        
        # Name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("人物名称")
        layout.addRow("名称:", self.name_edit)
        
        # Role
        self.role_combo = QComboBox()
        self.role_combo.addItems(["主角", "配角", "反派", "其他"])
        layout.addRow("角色类型:", self.role_combo)
        
        # Alias
        self.alias_edit = QLineEdit()
        self.alias_edit.setPlaceholderText("别名/绰号")
        layout.addRow("别名:", self.alias_edit)
        
        # Appearance
        self.appearance_edit = QTextEdit()
        self.appearance_edit.setMaximumHeight(60)
        layout.addRow("外貌:", self.appearance_edit)
        
        # Personality
        self.personality_edit = QTextEdit()
        self.personality_edit.setMaximumHeight(60)
        layout.addRow("性格:", self.personality_edit)
        
        # Background
        self.background_edit = QTextEdit()
        self.background_edit.setMaximumHeight(80)
        layout.addRow("背景:", self.background_edit)
        
        # Current location
        self.location_edit = QLineEdit()
        self.location_edit.setPlaceholderText("当前位置")
        layout.addRow("位置:", self.location_edit)
        
        # Cultivation realm (for xianxia)
        self.realm_edit = QLineEdit()
        self.realm_edit.setPlaceholderText("修炼境界")
        layout.addRow("境界:", self.realm_edit)
        
        # Level
        self.level_spin = QSpinBox()
        self.level_spin.setMinimum(1)
        self.level_spin.setMaximum(9999)
        layout.addRow("等级:", self.level_spin)
        
        # Alive status
        self.alive_check = QComboBox()
        self.alive_check.addItems(["存活", "已死亡"])
        layout.addRow("状态:", self.alive_check)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
    
    def _populate_data(self):
        """Populate fields with existing data."""
        self.name_edit.setText(self.character_data.get("name", ""))
        
        role = self.character_data.get("role", "")
        if role in ["主角", "配角", "反派", "其他"]:
            self.role_combo.setCurrentText(role)
        
        self.alias_edit.setText(self.character_data.get("alias", ""))
        self.appearance_edit.setText(self.character_data.get("appearance", ""))
        self.personality_edit.setText(self.character_data.get("personality", ""))
        self.background_edit.setText(self.character_data.get("background", ""))
        self.location_edit.setText(self.character_data.get("current_location", ""))
        self.realm_edit.setText(self.character_data.get("cultivation_realm", ""))
        self.level_spin.setValue(self.character_data.get("level", 1))
        
        if not self.character_data.get("is_alive", True):
            self.alive_check.setCurrentText("已死亡")
    
    def get_data(self) -> dict:
        """Get character data from form.
        
        Returns:
            Dict of character data
        """
        return {
            "name": self.name_edit.text(),
            "role": self.role_combo.currentText(),
            "alias": self.alias_edit.text(),
            "appearance": self.appearance_edit.toPlainText(),
            "personality": self.personality_edit.toPlainText(),
            "background": self.background_edit.toPlainText(),
            "current_location": self.location_edit.text(),
            "cultivation_realm": self.realm_edit.text(),
            "level": self.level_spin.value(),
            "is_alive": self.alive_check.currentText() == "存活",
        }


class ProjectPanel(QWidget):
    """Panel for managing projects and characters."""
    
    # Signals
    project_selected = pyqtSignal(int)  # Project ID
    chapter_selected = pyqtSignal(int)  # Chapter ID
    
    def __init__(self):
        """Initialize project panel."""
        super().__init__()
        
        self._current_project_id = None
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI components."""
        layout = QHBoxLayout(self)
        
        # Left - Projects list
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        left_layout.addWidget(QLabel("项目列表:"))
        
        self.project_list = QListWidget()
        self.project_list.itemClicked.connect(self._on_project_clicked)
        left_layout.addWidget(self.project_list)
        
        # Project buttons
        proj_btn_layout = QHBoxLayout()
        
        self.new_project_btn = QPushButton("新建")
        self.new_project_btn.clicked.connect(self._on_new_project)
        proj_btn_layout.addWidget(self.new_project_btn)
        
        self.edit_project_btn = QPushButton("编辑")
        self.edit_project_btn.clicked.connect(self._on_edit_project)
        self.edit_project_btn.setEnabled(False)
        proj_btn_layout.addWidget(self.edit_project_btn)
        
        self.delete_project_btn = QPushButton("删除")
        self.delete_project_btn.clicked.connect(self._on_delete_project)
        self.delete_project_btn.setEnabled(False)
        proj_btn_layout.addWidget(self.delete_project_btn)
        
        left_layout.addLayout(proj_btn_layout)
        
        # Middle - Chapters list
        middle_widget = QWidget()
        middle_layout = QVBoxLayout(middle_widget)
        
        middle_layout.addWidget(QLabel("章节列表:"))
        
        self.chapter_list = QListWidget()
        self.chapter_list.itemClicked.connect(self._on_chapter_clicked)
        middle_layout.addWidget(self.chapter_list)
        
        # Chapter info
        self.chapter_info_label = QLabel("未选择章节")
        middle_layout.addWidget(self.chapter_info_label)
        
        middle_layout.addStretch()
        
        # Right - Characters/Outlines
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Characters section
        right_layout.addWidget(QLabel("人物列表:"))
        
        self.character_list = QListWidget()
        right_layout.addWidget(self.character_list)
        
        char_btn_layout = QHBoxLayout()
        
        self.new_char_btn = QPushButton("新建人物")
        self.new_char_btn.clicked.connect(self._on_new_character)
        self.new_char_btn.setEnabled(False)
        char_btn_layout.addWidget(self.new_char_btn)
        
        self.edit_char_btn = QPushButton("编辑")
        self.edit_char_btn.clicked.connect(self._on_edit_character)
        self.edit_char_btn.setEnabled(False)
        char_btn_layout.addWidget(self.edit_char_btn)
        
        right_layout.addLayout(char_btn_layout)
        
        # Stats display
        stats_group = QGroupBox("项目统计")
        stats_layout = QFormLayout()
        
        self.total_words_label = QLabel("0")
        stats_layout.addRow("总字数:", self.total_words_label)
        
        self.total_chapters_label = QLabel("0")
        stats_layout.addRow("章节数:", self.total_chapters_label)
        
        self.total_cost_label = QLabel("$0.00")
        stats_layout.addRow("总消耗:", self.total_cost_label)
        
        stats_group.setLayout(stats_layout)
        right_layout.addWidget(stats_group)
        
        # Split layout
        layout.addWidget(left_widget, 1)
        layout.addWidget(middle_widget, 1)
        layout.addWidget(right_widget, 1)
    
    # Event handlers
    def _on_project_clicked(self, item):
        """Handle project list click."""
        # Extract project ID from item
        project_id = item.data(Qt.ItemDataRole.UserRole)
        if project_id:
            self._current_project_id = project_id
            self.project_selected.emit(project_id)
            self.edit_project_btn.setEnabled(True)
            self.delete_project_btn.setEnabled(True)
            self.new_char_btn.setEnabled(True)
    
    def _on_chapter_clicked(self, item):
        """Handle chapter list click."""
        chapter_id = item.data(Qt.ItemDataRole.UserRole)
        if chapter_id:
            self.chapter_selected.emit(chapter_id)
    
    def _on_new_project(self):
        """Handle new project button."""
        dialog = ProjectDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            # Emit signal or call callback to create project
            self.project_created.emit(data)
    
    def _on_edit_project(self):
        """Handle edit project button."""
        if not self._current_project_id:
            return
        
        # Get project data and show dialog
        # This would typically fetch from database
        dialog = ProjectDialog(self, {})
        if dialog.exec():
            data = dialog.get_data()
            self.project_updated.emit(self._current_project_id, data)
    
    def _on_delete_project(self):
        """Handle delete project button."""
        pass
    
    def _on_new_character(self):
        """Handle new character button."""
        if not self._current_project_id:
            return
        
        dialog = CharacterDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            self.character_created.emit(self._current_project_id, data)
    
    def _on_edit_character(self):
        """Handle edit character button."""
        pass
    
    # Public methods
    def add_project(self, project_id: int, name: str):
        """Add a project to the list.
        
        Args:
            project_id: Project ID
            name: Project name
        """
        item = QListWidgetItem(name)
        item.setData(Qt.ItemDataRole.UserRole, project_id)
        self.project_list.addItem(item)
    
    def clear_projects(self):
        """Clear all projects."""
        self.project_list.clear()
    
    def add_chapter(self, chapter_id: int, number: int, title: str, is_verified: bool):
        """Add a chapter to the list.
        
        Args:
            chapter_id: Chapter ID
            number: Chapter number
            title: Chapter title
            is_verified: Whether chapter is verified
        """
        text = f"第{number}章 {title or '未命名'}"
        if is_verified:
            text += " ✓"
        
        item = QListWidgetItem(text)
        item.setData(Qt.ItemDataRole.UserRole, chapter_id)
        
        if not is_verified:
            item.setBackground(QColor(255, 255, 200))
        
        self.chapter_list.addItem(item)
    
    def clear_chapters(self):
        """Clear all chapters."""
        self.chapter_list.clear()
    
    def add_character(self, character_id: int, name: str, role: str):
        """Add a character to the list.
        
        Args:
            character_id: Character ID
            name: Character name
            role: Character role
        """
        text = f"{name} ({role})"
        item = QListWidgetItem(text)
        item.setData(Qt.ItemDataRole.UserRole, character_id)
        self.character_list.addItem(item)
    
    def clear_characters(self):
        """Clear all characters."""
        self.character_list.clear()
    
    def update_stats(self, total_words: int, total_chapters: int, total_cost: float):
        """Update project statistics.
        
        Args:
            total_words: Total word count
            total_chapters: Total chapter count
            total_cost: Total cost in USD
        """
        self.total_words_label.setText(f"{total_words:,}")
        self.total_chapters_label.setText(str(total_chapters))
        self.total_cost_label.setText(f"${total_cost:.2f}")
    
    def set_chapter_info(self, number: int, title: str, word_count: int, verified: bool):
        """Set chapter information.
        
        Args:
            number: Chapter number
            title: Chapter title
            word_count: Word count
            verified: Whether verified
        """
        status = "已确认" if verified else "待确认"
        self.chapter_info_label.setText(
            f"第{number}章 {title}\n字数: {word_count} | 状态: {status}"
        )


# Add QColor import at top
from PyQt6.QtGui import QColor

# Add signals to class
from PyQt6.QtCore import pyqtSignal as _pyqtSignal
ProjectPanel.project_created = _pyqtSignal(dict)
ProjectPanel.project_updated = _pyqtSignal(int, dict)
ProjectPanel.character_created = _pyqtSignal(int, dict)
