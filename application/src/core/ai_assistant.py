"""AI assistant for managing project analysis and code generation."""

import json
import os
from datetime import datetime
from typing import Any, Dict

import anthropic
import openai
import pinecone
from langchain.embeddings import OpenAIEmbeddings


class AIAssistant:
    """Manages AI-powered code generation and analysis tasks."""

    def __init__(self):
        """Initialize AI assistant with required API clients."""
        self.openai_client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.claude_client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        self.embeddings = OpenAIEmbeddings()

        # Initialize Pinecone
        pinecone.init(
            api_key=os.getenv("PINECONE_API_KEY"),
            environment=os.getenv("PINECONE_ENVIRONMENT")
        )
        self.index_name = "ai-sdlc-tasks"
        if self.index_name not in pinecone.list_indexes():
            pinecone.create_index(
                name=self.index_name,
                dimension=1536,
                metric="cosine"
            )
        self.index = pinecone.Index(self.index_name)

    async def select_model(self, task_type: str) -> tuple:
        """Select the most appropriate AI model based on task type.

        Args:
            task_type: Type of task to select model for

        Returns:
            tuple: (model_name, client) pair for the selected model
        """
        default = ("gpt-4-turbo-preview", self.openai_client)
        model_mapping = {
            "requirement_analysis": default,
            "code_generation": default,
            "code_review": ("claude-3-opus", self.claude_client),
            "testing": ("mistral-7b", None),  # For Mistral integration
        }
        return model_mapping.get(task_type, default)

    async def analyze_requirements(
        self,
        project_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze project requirements and generate structured documentation.

        Args:
            project_data: Dict containing project details and
                requirements

        Returns:
            Dict containing analysis results and metadata
        """
        model, client = await self.select_model("requirement_analysis")

        # Create prompt for requirement analysis
        # Format requirements analysis prompt
        name = project_data.get('name')
        desc = project_data.get('description')
        reqs = json.dumps(project_data.get('requirements', []))

        prompt = (
            "Analyze the following project requirements and generate "
            "structured documentation:\n"
            f"Project Name: {name}\n"
            f"Description: {desc}\n"
            f"Requirements: {reqs}\n\n"
            "Please provide:\n"
            "1. Functional requirements breakdown\n"
            "2. Technical specifications\n"
            "3. Dependencies and constraints\n"
            "4. Risk assessment\n"
            "5. Implementation timeline"
        )
        
        try:
            # Generate analysis using selected model
            messages = [{"role": "user", "content": prompt}]
            if isinstance(client, openai.OpenAI):
                completion = await client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=2000
                )
                analysis = completion.choices[0].message.content
            elif isinstance(client, anthropic.Anthropic):
                msg = await client.messages.create(
                    model=model,
                    max_tokens=2000,
                    messages=messages
                )
                analysis = msg.content[0].text
            
            # Store analysis in vector store
            query_text = analysis[:1000]  # Limit text length
            embedding = await self.embeddings.aembed_query(query_text)
            timestamp = datetime.utcnow()
            vector_id = f"req-{timestamp.timestamp()}"

            # Create vector metadata
            metadata = {
                "project_id": project_data.get("id"),
                "type": "requirement_analysis",
                "timestamp": timestamp.isoformat()
            }

            # Store in Pinecone
            vector = {
                "id": vector_id,
                "values": embedding,
                "metadata": metadata
            }
            self.index.upsert(vectors=[vector])

            # Parse analysis result
            parsed_analysis = (
                json.loads(analysis)
                if isinstance(analysis, str)
                else analysis
            )
            return {
                "status": "success",
                "analysis": parsed_analysis,
                "model_used": model
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "model_used": model
            }

    async def assess_project_risks(self, project_id: int) -> Dict[str, Any]:
        """Perform risk assessment and feasibility analysis.

        Args:
            project_id: ID of the project to assess

        Returns:
            Dict containing risk assessment results and metadata
        """
        # Retrieve project context from vector store
        similar_projects = self.index.query(
            vector=[0] * 1536,  # Would use actual project embedding
            top_k=5,
            include_metadata=True
        )

        model, client = await self.select_model("requirement_analysis")

        # Format risk assessment prompt
        similar = json.dumps(similar_projects)
        prompt = (
            "Based on the project context and similar projects, perform a "
            "risk assessment and feasibility analysis.\n"
            f"Project ID: {project_id}\n"
            f"Similar Projects: {similar}\n\n"
            "Please provide:\n"
            "1. Technical risks and mitigation strategies\n"
            "2. Resource requirements and constraints\n"
            "3. Timeline feasibility\n"
            "4. Cost estimation\n"
            "5. Critical success factors"
        )
        
        try:
            # Generate assessment using selected model
            messages = [{"role": "user", "content": prompt}]
            if isinstance(client, openai.OpenAI):
                completion = await client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=2000
                )
                assessment = completion.choices[0].message.content
            elif isinstance(client, anthropic.Anthropic):
                msg = await client.messages.create(
                    model=model,
                    max_tokens=2000,
                    messages=messages
                )
                assessment = msg.content[0].text

            # Parse assessment result
            parsed_assessment = (
                json.loads(assessment)
                if isinstance(assessment, str)
                else assessment
            )
            
            return {
                "status": "success",
                "assessment": parsed_assessment,
                "model_used": model
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "model_used": model
            }
