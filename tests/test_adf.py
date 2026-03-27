# Internal imports
from jira.adf import markdown_to_adf


class TestBlockNodes:
    """Block-level Markdown elements → ADF top-level nodes."""
    def test_plain_text(self):
        result = markdown_to_adf("Hello world")
        assert result == {
            "type": "doc",
            "version": 1,
            "content": [
                {"type": "paragraph", "content": [{"type": "text", "text": "Hello world"}]},
            ],
        }

    def test_heading_levels(self):
        for level in range(1, 7):
            result = markdown_to_adf(f"{'#' * level} Title")
            assert result["content"] == [
                {"type": "heading", "attrs": {"level": level}, "content": [{"type": "text", "text": "Title"}]},
            ]

    def test_code_block_with_language(self):
        result = markdown_to_adf("```python\nprint('hi')\n```")
        assert result["content"] == [
            {
                "type": "codeBlock",
                "attrs": {"language": "python"},
                "content": [{"type": "text", "text": "print('hi')\n"}],
            },
        ]

    def test_code_block_without_language(self):
        result = markdown_to_adf("```\nplain code\n```")
        assert result["content"] == [
            {"type": "codeBlock", "content": [{"type": "text", "text": "plain code\n"}]},
        ]

    def test_blockquote(self):
        result = markdown_to_adf("> quoted text")
        assert result["content"] == [
            {"type": "blockquote", "content": [
                {"type": "paragraph", "content": [{"type": "text", "text": "quoted text"}]},
            ]},
        ]

    def test_thematic_break(self):
        result = markdown_to_adf("---")
        assert result["content"] == [{"type": "rule"}]

    def test_multiple_blocks(self):
        result = markdown_to_adf("# Title\n\nA paragraph.\n\n---")
        assert result["content"] == [
            {"type": "heading", "attrs": {"level": 1}, "content": [{"type": "text", "text": "Title"}]},
            {"type": "paragraph", "content": [{"type": "text", "text": "A paragraph."}]},
            {"type": "rule"},
        ]




class TestInlineMarks:
    """Inline Markdown formatting → ADF text nodes with marks."""

    def test_bold(self):
        result = markdown_to_adf("**bold**")
        assert result["content"] == [
            {"type": "paragraph", "content": [
                {"type": "text", "text": "bold", "marks": [{"type": "strong"}]},
            ]},
        ]

    def test_italic(self):
        result = markdown_to_adf("*italic*")
        assert result["content"] == [
            {"type": "paragraph", "content": [
                {"type": "text", "text": "italic", "marks": [{"type": "em"}]},
            ]},
        ]

    def test_inline_code(self):
        result = markdown_to_adf("`code`")
        assert result["content"] == [
            {"type": "paragraph", "content": [
                {"type": "text", "text": "code", "marks": [{"type": "code"}]},
            ]},
        ]

    def test_strikethrough(self):
        result = markdown_to_adf("~~deleted~~")
        assert result["content"] == [
            {"type": "paragraph", "content": [
                {"type": "text", "text": "deleted", "marks": [{"type": "strike"}]},
            ]},
        ]

    def test_nested_bold_and_italic(self):
        result = markdown_to_adf("***both***")
        marks = result["content"][0]["content"][0]["marks"]
        mark_types = {m["type"] for m in marks}
        assert mark_types == {"strong", "em"}

    def test_mixed_inline(self):
        result = markdown_to_adf("plain **bold** plain")
        content = result["content"][0]["content"]
        assert content[0] == {"type": "text", "text": "plain "}
        assert content[1] == {"type": "text", "text": "bold", "marks": [{"type": "strong"}]}
        assert content[2] == {"type": "text", "text": " plain"}


class TestLinks:
    """Markdown links → ADF text nodes with link marks."""

    def test_simple_link(self):
        result = markdown_to_adf("[click here](https://example.com)")
        assert result["content"] == [
            {"type": "paragraph", "content": [
                {"type": "text", "text": "click here", "marks": [
                    {"type": "link", "attrs": {"href": "https://example.com"}},
                ]},
            ]},
        ]

    def test_bold_link(self):
        result = markdown_to_adf("**[bold link](https://example.com)**")
        marks = result["content"][0]["content"][0]["marks"]
        mark_types = {m["type"] for m in marks}
        assert mark_types == {"strong", "link"}


class TestLists:
    """Markdown lists → ADF bulletList/orderedList with listItem nodes."""

    def test_bullet_list(self):
        result = markdown_to_adf("- alpha\n- beta")
        assert result["content"] == [
            {"type": "bulletList", "content": [
                {"type": "listItem", "content": [
                    {"type": "paragraph", "content": [{"type": "text", "text": "alpha"}]},
                ]},
                {"type": "listItem", "content": [
                    {"type": "paragraph", "content": [{"type": "text", "text": "beta"}]},
                ]},
            ]},
        ]

    def test_ordered_list(self):
        result = markdown_to_adf("1. first\n2. second")
        assert result["content"] == [
            {"type": "orderedList", "content": [
                {"type": "listItem", "content": [
                    {"type": "paragraph", "content": [{"type": "text", "text": "first"}]},
                ]},
                {"type": "listItem", "content": [
                    {"type": "paragraph", "content": [{"type": "text", "text": "second"}]},
                ]},
            ]},
        ]

    def test_nested_list(self):
        result = markdown_to_adf("- parent\n  - child")
        outer = result["content"][0]
        assert outer["type"] == "bulletList"
        first_item = outer["content"][0]
        assert first_item["type"] == "listItem"
        # First item has paragraph + nested list
        assert first_item["content"][0]["type"] == "paragraph"
        assert first_item["content"][1]["type"] == "bulletList"
        nested_item = first_item["content"][1]["content"][0]
        assert nested_item["content"][0] == {"type": "paragraph", "content": [{"type": "text", "text": "child"}]}
