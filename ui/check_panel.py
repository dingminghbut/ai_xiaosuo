"""Check panel for displaying content check results."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QTextEdit, QGroupBox,
    QScrollArea, QFrame, QListWidget, QListWidgetItem,
    QProgressBar, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor


class CheckPanel(QWidget):
    """Panel for displaying content check results."""
    
    # Signals
    check_requested = pyqtSignal()  # Request content check
    
    def __init__(self):
        """Initialize check panel."""
        super().__init__()
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        
        # Top controls
        top_layout = QHBoxLayout()
        
        self.check_btn = QPushButton("开始检查")
        self.check_btn.clicked.connect(self._on_check)
        top_layout.addWidget(self.check_btn)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        top_layout.addWidget(self.progress_bar)
        
        top_layout.addStretch()
        
        # Scores display
        self.score_label = QLabel("质量评分: --")
        top_layout.addWidget(self.score_label)
        
        layout.addLayout(top_layout)
        
        # Results tabs
        self.tabs = QScrollArea()
        self.tabs.setWidgetResizable(True)
        
        results_widget = QWidget()
        results_layout = QVBoxLayout(results_widget)
        
        # Consistency check results
        consistency_group = QGroupBox("一致性检查")
        consistency_layout = QVBoxLayout()
        
        self.consistency_score_label = QLabel("评分: --")
        consistency_layout.addWidget(self.consistency_score_label)
        
        self.consistency_list = QListWidget()
        consistency_layout.addWidget(self.consistency_list)
        
        consistency_group.setLayout(consistency_layout)
        results_layout.addWidget(consistency_group)
        
        # Content filter results
        filter_group = QGroupBox("违禁词检查")
        filter_layout = QVBoxLayout()
        
        self.filter_status_label = QLabel("状态: 未检查")
        filter_layout.addWidget(self.filter_status_label)
        
        self.filter_list = QListWidget()
        filter_layout.addWidget(self.filter_list)
        
        filter_group.setLayout(filter_layout)
        results_layout.addWidget(filter_group)
        
        # Style check results
        style_group = QGroupBox("文风检查")
        style_layout = QVBoxLayout()
        
        self.style_score_label = QLabel("评分: --")
        style_layout.addWidget(self.style_score_label)
        
        self.style_list = QListWidget()
        style_layout.addWidget(self.style_list)
        
        style_group.setLayout(style_layout)
        results_layout.addWidget(style_group)
        
        # Quality check results
        quality_group = QGroupBox("质量检查")
        quality_layout = QVBoxLayout()
        
        self.quality_score_label = QLabel("评分: --")
        quality_layout.addWidget(self.quality_score_label)
        
        self.quality_list = QListWidget()
        quality_layout.addWidget(self.quality_list)
        
        quality_group.setLayout(quality_layout)
        results_layout.addWidget(quality_group)
        
        results_layout.addStretch()
        
        self.tabs.setWidget(results_widget)
        layout.addWidget(self.tabs)
    
    def _on_check(self):
        """Handle check button click."""
        self.check_requested.emit()
    
    # Public methods
    def set_progress(self, progress: int):
        """Set progress bar.
        
        Args:
            progress: Progress percentage
        """
        if progress < 0:
            self.progress_bar.setVisible(False)
        else:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(progress)
    
    def display_consistency_results(self, score: float, issues: list):
        """Display consistency check results.
        
        Args:
            score: Consistency score (0-1)
            issues: List of issues
        """
        self.consistency_score_label.setText(f"评分: {score:.1%}")
        
        self.consistency_list.clear()
        
        for issue in issues:
            item_text = f"[{issue.severity.upper()}] {issue.description}"
            item = QListWidgetItem(item_text)
            
            if issue.severity == "high":
                item.setBackground(QColor(255, 200, 200))
            elif issue.severity == "medium":
                item.setBackground(QColor(255, 255, 200))
            
            self.consistency_list.addItem(item)
        
        if not issues:
            self.consistency_list.addItem("✓ 未发现问题")
    
    def display_filter_results(self, is_clean: bool, findings: list):
        """Display content filter results.
        
        Args:
            is_clean: Whether content is clean
            findings: List of prohibited words found
        """
        if is_clean:
            self.filter_status_label.setText("状态: ✓ 通过")
            self.filter_list.clear()
            self.filter_list.addItem("✓ 未检测到违禁内容")
        else:
            self.filter_status_label.setText(f"状态: ✗ 发现{len(findings)}处问题")
            self.filter_list.clear()
            
            for finding in findings:
                item_text = f"[{finding.category}] {finding.word}"
                if finding.get("context"):
                    item_text += f"\n  上下文: ...{finding['context']}..."
                
                item = QListWidgetItem(item_text)
                
                if finding.severity == "high":
                    item.setBackground(QColor(255, 180, 180))
                else:
                    item.setBackground(QColor(255, 230, 180))
                
                self.filter_list.addItem(item)
    
    def display_style_results(self, score: float, issues: list):
        """Display style check results.
        
        Args:
            score: Style score (0-1)
            issues: List of issues
        """
        self.style_score_label.setText(f"评分: {score:.1%}")
        
        self.style_list.clear()
        
        for issue in issues:
            item_text = f"[{issue.severity.upper()}] {issue.description}"
            item = QListWidgetItem(item_text)
            
            if issue.severity == "high":
                item.setBackground(QColor(255, 200, 200))
            elif issue.severity == "medium":
                item.setBackground(QColor(255, 255, 200))
            
            self.style_list.addItem(item)
        
        if not issues:
            self.style_list.addItem("✓ 文风良好")
    
    def display_quality_results(self, result: dict):
        """Display quality check results.
        
        Args:
            result: Quality check result dict
        """
        score = result.get("quality_score", 0)
        self.quality_score_label.setText(f"评分: {score:.1%}")
        
        self.quality_list.clear()
        
        # Word count
        word_count = result.get("word_count", 0)
        is_qualified = result.get("is_qualified", True)
        
        if is_qualified:
            self.quality_list.addItem(f"✓ 字数: {word_count}字")
        else:
            self.quality_list.addItem(f"✗ 字数不足: {word_count}字 (建议≥1800)")
        
        # Ending hook
        if result.get("has_ending_hook"):
            self.quality_list.addItem("✓ 有结尾钩子")
        else:
            self.quality_list.addItem("✗ 建议添加结尾钩子")
        
        # Good start
        if result.get("is_good_start"):
            self.quality_list.addItem("✓ 开头吸引人")
        else:
            self.quality_list.addItem("✗ 开头需改进")
        
        # Titles
        titles = result.get("titles", [])
        if titles:
            self.quality_list.addItem(f"\n候选标题 ({len(titles)}个):")
            for title in titles[:5]:
                self.quality_list.addItem(f"  • {title.title}")
        
        # Suggestions
        suggestions = result.get("suggestions", [])
        if suggestions:
            self.quality_list.addItem("\n建议:")
            for suggestion in suggestions:
                self.quality_list.addItem(f"  • {suggestion}")
    
    def display_overall_score(self, score: float):
        """Display overall quality score.
        
        Args:
            score: Overall score (0-1)
        """
        self.score_label.setText(f"质量评分: {score:.1%}")
        
        if score >= 0.8:
            self.score_label.setStyleSheet("color: green; font-weight: bold;")
        elif score >= 0.6:
            self.score_label.setStyleSheet("color: orange; font-weight: bold;")
        else:
            self.score_label.setStyleSheet("color: red; font-weight: bold;")
