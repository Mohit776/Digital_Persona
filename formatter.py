def format_profile(data):
    """Format raw profile data into structured text for RAG indexing.
    Returns a single string with all profile information.
    """
    profile = data.get("profile", {})
    posts = data.get("posts", [])
    
    sections = []
    
    # ── Basic Info ──
    first_name = profile.get("firstName", "")
    last_name = profile.get("lastName", "")
    name = f"{first_name} {last_name}".strip()
    headline = profile.get("headline", "")
    summary = profile.get("summary", "")
    location = profile.get("locationName", "") or profile.get("geoLocationName", "")
    industry = profile.get("industryName", "") or profile.get("industry", "")
    
    basic = []
    if name:
        basic.append(f"Full Name: {name}")
    if headline:
        basic.append(f"Professional Headline: {headline}")
    if location:
        basic.append(f"Location: {location}")
    if industry:
        basic.append(f"Industry: {industry}")
    if summary:
        basic.append(f"Professional Summary: {summary}")
    
    follower_count = profile.get("followerCount", 0)
    connections_count = profile.get("connectionsCount", 0)
    if follower_count:
        basic.append(f"LinkedIn Followers: {follower_count}")
    if connections_count:
        basic.append(f"LinkedIn Connections: {connections_count}")
    
    if basic:
        sections.append("PROFILE OVERVIEW\n" + "\n".join(basic))
    
    # ── Experience ──
    positions = profile.get("position", [])
    if isinstance(positions, list) and positions:
        exp_lines = ["WORK EXPERIENCE"]
        for pos in positions[:8]:
            if not isinstance(pos, dict):
                continue
            title = pos.get("title", "Unknown Role")
            company = pos.get("companyName", "Unknown Company")
            desc = pos.get("description", "")
            location_name = pos.get("locationName", "")
            
            # Build date string
            start = pos.get("timePeriod", {}).get("startDate", {})
            end = pos.get("timePeriod", {}).get("endDate", {})
            start_str = f"{start.get('month', '')}/{start.get('year', '')}" if start else ""
            end_str = f"{end.get('month', '')}/{end.get('year', '')}" if end else "Present"
            date_str = f" ({start_str} - {end_str})" if start_str else ""
            
            entry = f"Position: {title} at {company}{date_str}"
            if location_name:
                entry += f" | Location: {location_name}"
            exp_lines.append(entry)
            if desc:
                exp_lines.append(f"  Role Description: {desc}")
        
        sections.append("\n".join(exp_lines))
    
    # ── Education ──
    education = profile.get("education", [])
    if isinstance(education, list) and education:
        edu_lines = ["EDUCATION"]
        for edu in education[:5]:
            if not isinstance(edu, dict):
                continue
            school = edu.get("schoolName", "Unknown School")
            degree = edu.get("degreeName", "")
            field = edu.get("fieldOfStudy", "")
            activities = edu.get("activities", "")
            
            entry = f"School: {school}"
            if degree:
                entry += f" | Degree: {degree}"
            if field:
                entry += f" | Field: {field}"
            edu_lines.append(entry)
            if activities:
                edu_lines.append(f"  Activities: {activities}")
        
        sections.append("\n".join(edu_lines))
    
    # ── Skills ──
    skills = profile.get("skills", [])
    if isinstance(skills, list) and skills:
        skill_names = [s.get("name", "") for s in skills if isinstance(s, dict) and s.get("name")]
        if skill_names:
            sections.append(f"SKILLS AND EXPERTISE\nSkills: {', '.join(skill_names)}")
    
    # ── Certifications ──
    certifications = profile.get("certifications", [])
    if isinstance(certifications, list) and certifications:
        cert_lines = ["CERTIFICATIONS"]
        for cert in certifications[:5]:
            if not isinstance(cert, dict):
                continue
            cert_name = cert.get("name", "")
            authority = cert.get("authority", "")
            if cert_name:
                entry = f"Certification: {cert_name}"
                if authority:
                    entry += f" | Issued by: {authority}"
                cert_lines.append(entry)
        if len(cert_lines) > 1:
            sections.append("\n".join(cert_lines))
    
    # ── Languages ──
    languages = profile.get("languages", [])
    if isinstance(languages, list) and languages:
        lang_names = [l.get("name", "") for l in languages if isinstance(l, dict) and l.get("name")]
        if lang_names:
            sections.append(f"LANGUAGES\nLanguages: {', '.join(lang_names)}")
    
    # ── Volunteer ──
    volunteer = profile.get("volunteer", [])
    if isinstance(volunteer, list) and volunteer:
        vol_lines = ["VOLUNTEER EXPERIENCE"]
        for vol in volunteer[:3]:
            if not isinstance(vol, dict):
                continue
            role = vol.get("role", "")
            org = vol.get("companyName", "")
            cause = vol.get("cause", "")
            if role and org:
                entry = f"Role: {role} at {org}"
                if cause:
                    entry += f" | Cause: {cause}"
                vol_lines.append(entry)
        if len(vol_lines) > 1:
            sections.append("\n".join(vol_lines))
    
    # ── Posts ──
    # Handle nested posts structure
    if isinstance(posts, dict) and "posts" in posts:
        posts = posts["posts"]
    
    if isinstance(posts, list) and posts:
        post_lines = ["RECENT LINKEDIN POSTS AND ACTIVITY"]
        for i, post in enumerate(posts[:10], 1):
            if not isinstance(post, dict):
                continue
            content = (
                post.get("text") 
                or post.get("content") 
                or post.get("description") 
                or post.get("commentary", {}).get("text", "") if isinstance(post.get("commentary"), dict) else ""
            )
            if not content and isinstance(post.get("commentary"), str):
                content = post["commentary"]
            
            likes = post.get("numLikes", post.get("likeCount", 0))
            comments = post.get("numComments", post.get("commentCount", 0))
            
            if content:
                entry = f"Post {i}: {content.strip()}"
                if likes or comments:
                    entry += f"\n  Engagement: {likes} likes, {comments} comments"
                post_lines.append(entry)
        
        if len(post_lines) > 1:
            sections.append("\n".join(post_lines))
    
    return "\n\n".join(sections)