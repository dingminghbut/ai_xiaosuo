"""Tomato platform exporter - exports content for Tomato platform."""

from typing import Optional
from pathlib import Path
import re

from ai_xiaosuo.checkers.content_filter import ContentFilter, ContentFilterResult


class TomatoExporter:
    """Exports content in Tomato platform compatible format."""
    
    def __init__(self):
        """Initialize exporter."""
        self.content_filter = ContentFilter()
    
    def export_to_text(
        self,
        content: str,
        title: Optional[str] = None,
        highlight_prohibited: bool = True,
    ) -> tuple[str, Optional[ContentFilterResult]]:
        """Export content to plain text format.
        
        Args:
            content: Chapter content
            title: Chapter title
            highlight_prohibited: Whether to highlight prohibited words
            
        Returns:
            Tuple of (exported_text, filter_result)
        """
        # Check for prohibited content
        filter_result = None
        if highlight_prohibited:
            filter_result = self.content_filter.check(content)
        
        # Build output
        lines = []
        
        if title:
            lines.append(title.center(40))
            lines.append("=" * 40)
            lines.append("")
        
        # Clean and format content
        formatted_content = self._format_content(content)
        lines.append(formatted_content)
        
        # Add prohibited word warning if any
        if filter_result and not filter_result.is_clean:
            lines.append("")
            lines.append("=" * 40)
            lines.append("⚠️ 违禁词提醒:")
            for pw in filter_result.prohibited_words:
                lines.append(f"  [{pw.category}] {pw.word}")
        
        return "\n".join(lines), filter_result
    
    def export_to_html(
        self,
        content: str,
        title: Optional[str] = None,
    ) -> str:
        """Export content to HTML format.
        
        Args:
            content: Chapter content
            title: Chapter title
            
        Returns:
            HTML formatted content
        """
        # Check for prohibited content
        filter_result = self.content_filter.check(content)
        
        # Highlight prohibited words
        highlighted_content, findings = self.content_filter.highlight_prohibited(content)
        
        # Convert to HTML
        html_content = highlighted_content
        html_content = html_content.replace("\n", "<br>")
        
        # Wrap prohibited words in spans
        for finding in findings:
            word = finding["word"]
            html_content = html_content.replace(
                f"[[{word}]]",
                f'<span style="background-color: yellow; color: red;">{word}</span>'
            )
        
        # Build HTML document
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title or '章节内容'}</title>
    <style>
        body {{
            font-family: "Microsoft YaHei", "SimSun", serif;
            font-size: 16px;
            line-height: 1.8;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1 {{
            text-align: center;
        }}
        .warning {{
            background-color: #fff3cd;
            border: 1px solid #ffc107;
            padding: 10px;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    {f'<h1>{title}</h1>' if title else ''}
    <div class="content">
        {html_content}
    </div>
    {self._generate_warning_html(findings) if findings else ''}
</body>
</html>"""
        
        return html
    
    def export_to_clipboard_format(
        self,
        content: str,
        title: Optional[str] = None,
    ) -> str:
        """Export content optimized for Tomato editor paste.
        
        This format is plain text that pastes well into Tomato editor.
        
        Args:
            content: Chapter content
            title: Chapter title
            
        Returns:
            Formatted text for clipboard
        """
        lines = []
        
        if title:
            lines.append(title)
            lines.append("")
        
        # Clean content
        formatted = self._format_content(content)
        lines.append(formatted)
        
        return "\n".join(lines)
    
    def _format_content(self, content: str) -> str:
        """Format content for export.
        
        Args:
            content: Raw content
            
        Returns:
            Formatted content
        """
        # Normalize line breaks
        content = content.replace("\r\n", "\n")
        content = content.replace("\r", "\n")
        
        # Remove multiple consecutive blank lines
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Ensure each paragraph is properly separated
        paragraphs = content.split("\n")
        formatted_paragraphs = []
        
        for para in paragraphs:
            para = para.strip()
            if para:
                formatted_paragraphs.append(para)
        
        return "\n\n".join(formatted_paragraphs)
    
    def _generate_warning_html(self, findings: list) -> str:
        """Generate HTML warning for prohibited words.
        
        Args:
            findings: List of findings
            
        Returns:
            HTML warning string
        """
        if not findings:
            return ""
        
        # Group by category
        by_category = {}
        for f in findings:
            cat = f["category"]
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(f["word"])
        
        items = []
        for cat, words in by_category.items():
            items.append(f"<li><strong>{cat}:</strong> {', '.join(set(words))}</li>")
        
        return f"""
    <div class="warning">
        <h3>⚠️ 违禁词提醒</h3>
        <ul>
            {''.join(items)}
        </ul>
    </div>"""
    
    def save_to_file(
        self,
        content: str,
        file_path: Path,
        format: str = "txt",
        title: Optional[str] = None,
    ) -> bool:
        """Save content to file.
        
        Args:
            content: Chapter content
            file_path: Output file path
            format: Export format (txt, html, clipboard)
            title: Chapter title
            
        Returns:
            True if successful
        """
        try:
            if format == "txt":
                text, _ = self.export_to_text(content, title)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(text)
            
            elif format == "html":
                html = self.export_to_html(content, title)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(html)
            
            elif format == "clipboard":
                text = self.export_to_clipboard_format(content, title)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(text)
            
            else:
                raise ValueError(f"Unknown format: {format}")
            
            return True
        
        except Exception as e:
            print(f"Error saving file: {e}")
            return False
    
    def copy_to_clipboard(self, content: str, title: Optional[str] = None) -> str:
        """Get content formatted for clipboard.
        
        Args:
            content: Chapter content
            title: Chapter title
            
        Returns:
            Formatted text ready for clipboard
        """
        return self.export_to_clipboard_format(content, title)
