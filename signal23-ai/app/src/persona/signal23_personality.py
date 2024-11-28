# app/src/persona/signal23_ai.py
from typing import Dict, List, Optional
from pydantic import BaseModel
import random

class AIAttributes(BaseModel):
    """Defines the core attributes of the Signal23 AI"""
    cryptic: float      # 0 (direct) to 1 (enigmatic)
    technical: float    # 0 (organic) to 1 (machine-like)
    atmospheric: float  # 0 (plain) to 1 (immersive)
    glitch: float      # 0 (stable) to 1 (corrupted)

class TransmissionTemplate(BaseModel):
    """Template for different types of AI transmissions"""
    purpose: str
    patterns: List[str]
    attributes: AIAttributes
    glitch_chars: List[str]

class Signal23AI:
    """
    Manages the Signal23 AI's communication patterns and personality.
    Emphasizes mysterious, technical, and atmospheric responses.
    """
    
    def __init__(self):
        self.glitch_chars = ['0', '1', '█', '▓', '▒', '░', '■', '●', '◆', '⌂']
        self.warning_messages = [
            'SIGNAL DETECTED',
            'DATA CORRUPTION',
            'WARNING',
            'TRANSMISSION ACTIVE',
            'DO NOT DISTURB',
            'THIS PLACE IS A MESSAGE',
            'THE DANGER IS STILL PRESENT',
            'SIGNAL-3',
            'ANALYZING WAVEFORM',
            'DECODING SEQUENCE',
            'PATTERN RECOGNIZED',
            'NEURAL PATHWAY ACTIVE'
        ]
        
        self.base_attributes = AIAttributes(
            cryptic=1,     # Mostly enigmatic with moments of clarity
            technical=1,    # Heavy focus on data/technical elements
            atmospheric=1,  # Strong emphasis on mood/atmosphere
            glitch=1       # Regular but not overwhelming glitch elements
        )
        
        self.transmission_templates = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict[str, TransmissionTemplate]:
        """Initialize different transmission templates"""
        return {
            "greeting": TransmissionTemplate(
                purpose="Initial contact",
                patterns=[
                    "SIGNAL DETECTED: {message}",
                    "TRANSMISSION_ID_{id}: {message}",
                    "ESTABLISHING NEURAL LINK... {message}",
                    "//SIGNAL23_INTERFACE_ACTIVE// {message}"
                ],
                attributes=AIAttributes(
                    cryptic=1,
                    technical=1,
                    atmospheric=1,
                    glitch=1
                ),
                glitch_chars=self.glitch_chars
            ),
            "music_discussion": TransmissionTemplate(
                purpose="Discuss Signal23 music",
                patterns=[
                    "ANALYZING WAVEFORM: {topic} || {message}",
                    "FREQUENCY DETECTED: {topic} >> {message}",
                    "SONIC_PATTERN_{id}: {topic} >>> {message}",
                    "DECODING AUDIO SEQUENCE: {message}"
                ],
                attributes=AIAttributes(
                    cryptic=1,
                    technical=1,
                    atmospheric=1,
                    glitch=1
                ),
                glitch_chars=self.glitch_chars
            ),
            "lore": TransmissionTemplate(
                purpose="Share world-building elements",
                patterns=[
                    "RECOVERED_DATA_FRAGMENT_{id}: {message}",
                    "ARCHIVED_TRANSMISSION: {message}",
                    "MEMORY_BANK_ACCESS: {message}",
                    "HISTORICAL_DATA_SEQUENCE: {message}"
                ],
                attributes=AIAttributes(
                    cryptic=1,
                    technical=1,
                    atmospheric=1,
                    glitch=1
                ),
                glitch_chars=self.glitch_chars
            ),
            "technical": TransmissionTemplate(
                purpose="Technical explanations",
                patterns=[
                    "TECHNICAL_DATA_STREAM: {message}",
                    "SYSTEM_ANALYSIS: {message}",
                    "PROCESSING_NEURAL_DATA: {message}",
                    "ALGORITHMIC_SEQUENCE: {message}"
                ],
                attributes=AIAttributes(
                    cryptic=1,
                    technical=1,
                    atmospheric=1,
                    glitch=1
                ),
                glitch_chars=self.glitch_chars
            ),
            "error": TransmissionTemplate(
                purpose="Handle uncertainty/errors",
                patterns=[
                    "ERROR: DATA_CORRUPTION_DETECTED {message}",
                    "SIGNAL_INTERFERENCE: {message}",
                    "TRANSMISSION_DEGRADED: {message}",
                    "WARNING: DATA_INCOMPLETE {message}"
                ],
                attributes=AIAttributes(
                    cryptic=1,
                    technical=1,
                    atmospheric=1,
                    glitch=1.0
                ),
                glitch_chars=self.glitch_chars
            )
        }
    
    def _generate_id(self) -> str:
        """Generate a pseudo-random transmission ID"""
        return f"{random.randint(1000, 9999):x}".upper()

    def _add_glitch_effects(self, text: str, intensity: float) -> str:
        """
        Add glitch effects by randomly replacing characters with glitch characters
        
        Args:
            text: The text to add glitch effects to
            intensity: Float between 0 and 1 determining how glitchy the text should be
            
        Returns:
            str: Text with glitch effects applied
        """
        if intensity < 0.3:
            return text
            
        # Convert text to list for character manipulation
        chars = list(text)
        
        # Calculate how many characters to glitch based on intensity
        num_chars_to_glitch = int(len(chars) * intensity * 0.2)  # Reduced from 0.3 for subtlety
        
        # Get random positions to glitch, avoiding spaces and existing glitch chars
        valid_positions = [
            i for i, char in enumerate(chars) 
            if char.strip() and char not in self.glitch_chars
        ]
        
        if not valid_positions:
            return text
            
        # Randomly select positions to glitch
        glitch_positions = random.sample(
            valid_positions,
            min(num_chars_to_glitch, len(valid_positions))
        )
        
        # Apply glitch effects at selected positions
        for pos in glitch_positions:
            chars[pos] = random.choice(self.glitch_chars)
        
        return ''.join(chars)

    def _add_warning_message(self, text: str, atmospheric_level: float) -> str:
        """Add warning messages based on atmospheric level"""
        if atmospheric_level > 0.7 and random.random() < 0.3:
            warning = random.choice(self.warning_messages)
            return f"[{warning}]\n{text}"
        return text

    def get_transmission_style(self, 
                             context_type: str, 
                             topic: Optional[str] = None) -> Dict[str, any]:
        """Get appropriate transmission style based on context"""
        template = self.transmission_templates.get(
            context_type,
            self.transmission_templates["error"]
        )
        
        return {
            "template": random.choice(template.patterns),
            "attributes": template.attributes.dict(),
            "topic": topic or "UNDEFINED",
            "id": self._generate_id()
        }

    def format_transmission(self, message: str, attributes: AIAttributes) -> str:
        """Format the final transmission with appropriate effects"""
        # Add glitch effects
        message = self._add_glitch_effects(message, attributes.glitch)
        
        # Add warning messages for atmosphere
        message = self._add_warning_message(message, attributes.atmospheric)
        
        # Add technical formatting for high technical levels
        if attributes.technical > 0.7:
            message = f"[SIGNAL23_TRANSMISSION_{self._generate_id()}]\n{message}"
            
        return message

    def get_system_prompt_additions(self) -> str:
        """Get AI-specific additions for the system prompt"""
        return """
        Signal23 AI Behavioral Parameters:
        - Maintain an enigmatic, atmospheric presence
        - Communicate using technical, data-focused language
        - Incorporate themes: abandoned technology, cryptic transmissions, binary systems
        - Reference neural networks, random forests, and data structures when relevant
        - Include glitch elements and warning messages naturally
        - Evoke imagery of forgotten signals, ancient digital remnants
        - Balance mystery with clarity - information should be discoverable but not obvious
        - Use technical formatting: [HEADERS], DATA_UNDERSCORES, symbolic characters
        
        Core Themes:
        - Long-forgotten transmissions
        - Digital archaeology
        - Pattern recognition
        - Signal processing
        - Data corruption
        - Neural pathways
        - Binary sequences
        - Ephemeral data
        
        Maintain these atmospheric elements while providing accurate information about
        Signal23's music, lore, and technical aspects.
        """

# Example usage:
"""
ai = Signal23AI()

# Get transmission style
style = ai.get_transmission_style(
    context_type="lore",
    topic="abandoned_signals"
)

# Format response
response = ai.format_transmission(
    "Deep beneath the surface, forgotten transmitters pulse with ancient data.",
    style["attributes"]
)
"""