from jinja2 import Template


briefing_template = """
<html>
    <div style="font-family: Overpass; display: flex; margin-left: auto; margin-right: auto;">
        <div style="width: 30%;">
            <img src="{{ profile_picture }}" alt="Profile Picture">
        </div>
        <div style="width: 70%; margin-left: 24px;">
            <div>
                <span style="font-size: 32px; font-weight: 500; ">{{ name }}</span>
            </div>

            <div>
                <span>{{ position }}</span>
            </div>

            <hr style="margin-top:10px; margin-bottom:10px;" />

            <div style="font-family: Overpass; display: flex; margin-left: auto; margin-right: auto;">
                <div style="width: 22%;">
                    <p style="line-height: 0.5;font-weight:500;">h-index</p>
                    <p>{{ h_index }}</p>
                </div>

                <div style="width:78%;">
                    <p style="line-height: 0.5;">Research Interests</p>
                    <p>{{ research_interests }}</p>
                </div>
            </div>

            <hr style=" margin-bottom:10px;" />
            <div>
                <span>Google Scholar Profile: <a href="{{ scholar_link }}">Link</a></span>
            </div>
            <div>
                <span>Homepage: <a href="{{ homepage_link }}">Link</a></span>
            </div>
        </div>
    </div>
</html>
"""


def fill_template(template, contents):
    return Template(template).render(contents)
