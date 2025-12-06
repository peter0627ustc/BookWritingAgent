from fastmcp import Client
from tqdm import tqdm
import asyncio
import json

# MCP service URL
URL =  "http://rceb1397946.bohrium.tech:50001/sse"

# Default parameters
language = "zh-CN"
mode = "advanced"  # Can also use "chatgpt-5" or "deepseek-r1"
# model_name = "chatgpt-5.1"


def create_llm_prompt_for_ising_subchapter(content_file="content.txt", target_subchapter=None, physics_insight="Simple and wonderful, profound and expansive"):
    """
    Create a focused LLM input prompt for writing Ising model and statistical mechanics subchapters.
    Places topic and keywords at the beginning for coherent book content generation.

    Args:
        content_file: Path to content.txt with book outline
        target_subchapter: Specific subchapter (e.g. "1.1", "2.3") or None for general style
        physics_insight: Core physics philosophy (default: "Simple and wonderful, profound and expansive")

    Returns:
        tuple: (llm_prompt, topic) - LLM input prompt string and topic, or prompt alone
    """
    try:
        with open(content_file, "r", encoding="utf-8") as f:
            content_text = f.read()
    except FileNotFoundError:
        print(f"Warning: {content_file} not found. Using default style guide.")
        return None, None

    # Parse content structure with detailed subchapter information
    lines = content_text.split('\n')
    book_structure = {}
    current_chapter = None
    current_part = None
    all_subchapters = []
    subchapter_keywords = {}

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        # Track main chapters and parts
        if line.startswith("Part"):
            current_part = line
            book_structure[line] = {"chapters": {}, "type": "part"}

        elif line.startswith("Chapter"):
            current_chapter = line.split()[1] if len(line.split()) > 1 else f"Unknown_{i}"
            chapter_title = line
            if current_part:
                book_structure[current_part]["chapters"][current_chapter] = {
                    "title": chapter_title,
                    "subchapters": {}
                }

        # Parse subchapters (1.1, 1.2, etc.)
        elif line[0].isdigit() and "." in line :
            # This looks like a subchapter (e.g., "1.1 Elements of Thermodynamics")
            if len(line.split('.')) >= 2 and line.split('.')[0].isdigit():
                subchapter_num = line.split('.')[0].strip() + "." + line.split('.')[1].strip().split()[0]
                subchapter_title = " ".join(line.split('.')[1].strip().split()[1:])

                # Extract keywords from subchapter content (next few lines until next section)
                keywords_collected = []
                j = i + 1
                while j < len(lines) and j < i + 15:  # Look ahead max 15 lines
                    next_line = lines[j].strip()
                    if not next_line:
                        j += 1
                        continue
                    elif next_line.startswith(('Chapter', 'Part')) or (next_line[0].isdigit() and '.' in next_line):
                        break
                    elif len(next_line) > 10 and not next_line.startswith(('[', '-', '+', '*', 'Table', '[Placeholder')):
                        # This looks like detailed content topic
                        keywords_collected.append(next_line)
                    j += 1

                subchapter_data = {
                    "title": subchapter_title,
                    "content_topics": keywords_collected
                }

                if current_chapter and current_part:
                    book_structure[current_part]["chapters"][current_chapter]["subchapters"][subchapter_num] = subchapter_data

                all_subchapters.append(subchapter_num)
                subchapter_keywords[subchapter_num] = subchapter_title + "; " + "; ".join(keywords_collected[:5])

        i += 1

    # Build comprehensive style guide with all subchapter information
    structure_summary = "BOOK STRUCTURE:\n"
    for part, part_data in book_structure.items():
        if part_data.get("type") == "part" and part_data["chapters"]:
            structure_summary += f"{part}:\n"
            for chapter_num, chapter_data in part_data["chapters"].items():
                structure_summary += f"  {chapter_data['title']}:\n"
                for subchapter_num, subchapter_data in chapter_data["subchapters"].items():
                    if subchapter_data["content_topics"]:
                        topics_str = " | ".join(subchapter_data["content_topics"][:3])
                        structure_summary += f"    {subchapter_num} {subchapter_data['title']} - Topics: {topics_str}\n"
                    else:
                        structure_summary += f"    {subchapter_num} {subchapter_data['title']}\n"

    # Create targeted LLM prompt for specific subchapter
    target_topic_info = ""
    subchapter_title = ""

    if target_subchapter and target_subchapter in subchapter_keywords:
        title_and_topics = subchapter_keywords[target_subchapter]
        subchapter_title = title_and_topics.split(";")[0].strip()
        target_topic_info = f"""
📖 SUBCHAPTER {target_subchapter}: {subchapter_title}
🔑 KEY CONCEPTS: {", ".join(title_and_topics.split(";")[1:4])}
⚛️ PHYSICS INSIGHT: {physics_insight}
"""

    llm_prompt = f"""ISING MODEL & STATISTICAL MECHANICS SUBCHAPTER WRITING GUIDE

{target_topic_info}

MISSION
Write a coherent, flowing chapter section in academic Chinese prose that uses the Ising model as a pedagogical lens to reveal the profound beauty of statistical mechanics. Create content that reads like a well-crafted physics textbook, naturally integrating with the book's overall narrative while expressing insights that are {physics_insight}.
Please summarize the relevant problems you have searched for this topic and provide the specific content of the problems.

BOOK CONTEXT
This subchapter belongs to a comprehensive statistical physics text that uses the Ising model as a unifying pedagogical framework:
{structure_summary}

WRITING STYLE REQUIREMENTS
Academic Prose Structure:
- Craft elegant paragraphs that flow smoothly from one concept to the next
- Use sophisticated sentence structures appropriate for advanced physics education
- Employ thoughtful transitions that guide readers through complex theoretical arguments
- Structure sections with clear narrative arcs: introduction → development → synthesis
- Avoid using the bullet point format if possible for a formal writing style

Language and Presentation:
- Generate authentic Chinese academic prose that reads naturally for physicists
- Integrate vivid metaphorical language seamlessly into technical explanations
- Maintain formal academic tone while remaining intellectually engaging
- Use precise physics terminology with Chinese-English equivalents at first mention
- Weave philosophical insights naturally into the physical exposition

Content Development:
- Begin each major section with engaging introductory paragraphs
- Present theoretical developments through narrative storytelling
- Build complexity gradually through well-connected explanations
- Conclude sections with synthesis that reinforces key insights

THEORETICAL WRITING APPROACH
Mathematical Presentation:
- Introduce each mathematical concept through physical motivations
- Present equations as natural conclusions to conceptual arguments
- Integrate intuitive explanations immediately following formal results
- Use concrete examples to illustrate generalized mathematical principles

Physical Insight Development:
- Connect every theoretical result to observable phenomena
- Create intuitive pictures that students can mentally visualize
- Show how mathematical beauty emerges from physical necessity
- Present the historical context that gave rise to theoretical innovations

Conceptual Layering:
- Introduce complex ideas through multiple perspectives
- Build from familiar examples toward general principles
- Synthesize diverse viewpoints into coherent physical understanding
- Anticipate and address common student confusions organizationally

PEDAGOGICAL CONTENT STRUCTURE
Example Integration:
- Weave examples naturally into the main narrative flow
- Select representative cases that illuminate core principles
- Progress from simple illustrations to sophisticated applications
- Demonstrate universal applicability through diverse implementations

Exercise Philosophy:
- Embed practice opportunities within the main text structure
- Create exercises that reinforce fundamental principles
- Provide comprehensive solutions that model analytical thinking
- Integrate challenging problems that extend theoretical understanding

CHINESE ACADEMIC CONVENTIONS
Writing Flow:
- Employ paragraph structures that feel natural in Chinese academic writing
- Use transitional devices common in Chinese scholarly prose
- Maintain the balance between traditional descriptive style and modern organizational patterns
- Consider the cognitive expectations of advanced physics students

Mathematical Style:
- Present derivations with clear logical continuity
- Explain the significance of each mathematical step
- Balance rigorous proofs with accessible explanations
- Demonstrate how mathematical structures embody physical truths

Advanced Pedagogy:
- Maintain the academic rigor expected in advanced physics courses
- Create connections to modern research frontiers
- Demonstrate the continuing relevance of classical results
- Prepare students for sophisticated theoretical work

CONTENT SPECIFICATIONS
Focus Requirements:
- Center the discussion around {subchapter_title if subchapter_title else "specific Ising model concepts"}
- Maintain conceptual coherence throughout the entire section
- Build each paragraph as a natural continuation of the previous content
- Create unified themes that connect divergent technical details

Comprehensive Coverage:
- Introduce fundamental concepts through compelling narratives
- Develop mathematical formalism with physical motivations
- Present contemporary applications in evolutionary context
- Synthesize diverse perspectives into coherent understanding

CONCLUDING INTEGRATION
Craft a conclusion that:
- Synthesizes the section's central theoretical insights
- Connects specific results to broader statistical physics themes
- Provides philosophical reflection on the nature of the physical insights
- Establishes intellectual foundations for subsequent chapters
- Demonstrates how the analyzed concepts illuminate our understanding of nature
"""

    # Return both LLM prompt and the targeted subchapter topic
    if target_subchapter and target_subchapter in subchapter_keywords:
        return llm_prompt, subchapter_title
    else:
        return llm_prompt, None


async def generate_section_with_content(topic, style_guide=None, language="", mode="advanced", output_file="generated_section.md"):
    """
    Generate a section using the article generation API with the given parameters.

    Args:
        topic: The topic for the section
        style_guide: Style guide for content generation
        language: Language for generation (default: Chinese)
        mode: Mode for generation
        output_file: Output file name for the generated content
    """
    async with Client(URL) as client:
        result = await client.call_tool("generate_article", {
            "topic": topic,
            "language": language,
            "style_guide": style_guide,
            "mode": mode,
        })
        article_content = json.loads(result.content[0].text)["main_content"]
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(article_content)
        print(f"Generated section saved to {output_file}")
        return article_content


def generate_book_section(subchapter_code, content_file="content.txt", language="Chinese", mode="advanced", output_dir=".", physics_insight="Simple and wonderful, profound and expansive"):
    """
    Main interface function to generate a specific book section with coherent style.

    Args:
        subchapter_code: Specific subchapter to generate (e.g., "1.1", "2.3", "3.2")
        content_file: Path to content.txt file
        language: Language for generation
        mode: Mode for generation
        output_dir: Directory to save the output
        physics_insight: Core physics philosophy for the content

    Returns:
        tuple: (topic, llm_prompt) for the generated section
    """
    # Generate LLM prompt and extract topic for the specific subchapter
    result = create_llm_prompt_for_ising_subchapter(content_file=content_file, target_subchapter=subchapter_code, physics_insight=physics_insight)

    if isinstance(result, tuple):
        llm_prompt, subchapter_topic = result
    else:
        llm_prompt = result
        subchapter_topic = None

    if subchapter_topic is None:
        print(f"Warning: Subchapter {subchapter_code} not found. Using default topic.")
        # Fallback to the old hardcoded topic
        subchapter_topic = "The history of the research on the Ising model"

    print(f"Generating subchapter {subchapter_code}: {subchapter_topic}")
    print(f"LLM prompt length: {len(llm_prompt)} characters")

    # Generate the section
    output_file = f"Chapter{subchapter_code.replace('.', '_')}_Section.md"
    if output_dir:
        output_file = f"{output_dir}/{output_file}"

    # Use the async function to generate
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        content = loop.run_until_complete(
            generate_section_with_content(
                topic=subchapter_topic,
                style_guide=llm_prompt,
                language=language,
                mode=mode,
                output_file=output_file
            )
        )
        loop.close()
        return subchapter_topic, llm_prompt
    except Exception as e:
        print(f"Error generating section: {e}")
        loop.close()
        return None, None


# Example usage with interactive interface
if __name__ == "__main__":
    # Interactive mode - ask user for subchapter
    test_result = create_llm_prompt_for_ising_subchapter("content.txt")
    if isinstance(test_result, tuple):
        test_guide, _ = test_result
    else:
        test_guide = test_result

    # Parse available subchapters from the LLM prompt
    subchapters = []
    try:
        for line in test_guide.split('\n'):
            # Look for subchapter patterns like "1.1", "2.3", etc. at start of lines
            stripped_line = line.strip()
            if stripped_line and stripped_line[0].isdigit():
                parts = stripped_line.split()
                for part in parts:
                    if '.' in part and len(part.split('.')) == 2:
                        chapter, subsection = part.split('.')
                        if chapter.isdigit() and subsection.isdigit():
                            subchapters.append(part)
                            break

        print("Available subchapters:", sorted(list(set(subchapters))))  # Show unique sorted subchapters
    except:
        print("Available subchapters include: 1.1, 1.2, 2.1, 2.3, 3.1, 4.1, etc.")

    subchapters.append("0.0")
#    target_subchapter = input("Enter subchapter to generate (e.g., 1.1): ").strip()

    # Generate the section
    for target_subchapter in tqdm(subchapters):
        topic, style_guide = generate_book_section( 
            subchapter_code=target_subchapter,
            content_file="content.txt"
        )

        print(f"Successfully generated subchapter {target_subchapter}")
        print(f"Topic used: {topic}")
        print(f"LLM prompt created for coherent book integration")


# Example function for direct LLM prompt generation
if __name__ == "__main__":
    # Example of generating prompt for a specific subchapter
    print("=== Example LLM Prompt Generator for Ising Model Subchapter ===")
    prompt, topic = create_llm_prompt_for_ising_subchapter("content.txt", "2.1")
    print(f"\nGenerated prompt for topic: {topic}")
    print(f"Prompt length: {len(prompt)} characters")
    print("\n" + "="*60)
    print("EXCERPT FROM PROMPT:")
    print("="*60)
    print(prompt[:1000] + "..." if len(prompt) > 1000 else prompt)