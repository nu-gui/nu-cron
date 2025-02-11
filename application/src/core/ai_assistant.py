"""AI assistant for managing project analysis and code generation."""

from datetime import datetime
from typing import Dict, Any

import json
import os
import openai
import anthropic
import pinecone
from langchain.embeddings import OpenAIEmbeddings


class AIAssistant:
    """Manages AI-driven project analysis and code generation tasks."""

    def __init__(self):
        """Initialize AI assistant with required API clients.

        Sets up OpenAI, Anthropic, and Pinecone clients using env vars
        for authentication and configuration.
        """
        # Initialize API clients
        openai_key = os.getenv("OPENAI_API_KEY")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")

        self.openai_client = openai.OpenAI(api_key=openai_key)
        self.claude_client = anthropic.Anthropic(api_key=anthropic_key)
        self.embeddings = OpenAIEmbeddings()

        # Initialize Pinecone vector store
        pinecone_key = os.getenv("PINECONE_API_KEY")
        pinecone_env = os.getenv("PINECONE_ENVIRONMENT")
        pinecone.init(api_key=pinecone_key, environment=pinecone_env)

        # Set up index
        self.index_name = "ai-sdlc-tasks"
        if self.index_name not in pinecone.list_indexes():
            pinecone.create_index(
                name=self.index_name,
                dimension=1536,
                metric="cosine"
            )
        self.index = pinecone.Index(self.index_name)

    async def select_model(self, task_type: str) -> tuple[str, Any]:
        """Select the most appropriate AI model based on task type.

        Args:
            task_type: Type of task to select model for.

        Returns:
            Tuple containing:
                - model_name: Name of the AI model to use
                - client: API client instance for the model
        """
        default = ("gpt-4-turbo-preview", self.openai_client)
        model_mapping = {
            "requirement_analysis": default,
            "code_generation": default,
            "code_review": ("claude-3-opus", self.claude_client),
            "testing": ("mistral-7b", None),  # Placeholder
        }
        return model_mapping.get(task_type, default)

    async def analyze_requirements(
        self, project_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze project requirements and generate structured documentation.

        Args:
            project_data: Dictionary containing project details and
                requirements.

        Returns:
            Dictionary containing analysis results and model info.
        """
        model, client = await self.select_model("requirement_analysis")

        # Format project data for prompt
        name = project_data.get("name")
        desc = project_data.get("description")
        reqs = json.dumps(project_data.get("requirements", []))

        # Create prompt for requirement analysis
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
            if isinstance(client, openai.OpenAI):
                # Generate analysis using OpenAI
                completion = await client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=2000,
                )
                analysis = completion.choices[0].message.content
            elif isinstance(client, anthropic.Anthropic):
                # Generate analysis using Anthropic
                msg = await client.messages.create(
                    model=model,
                    max_tokens=2000,
                    messages=[{"role": "user", "content": prompt}],
                )
                analysis = msg.content[0].text

            # Store analysis in vector store
            query_text = analysis[:1000]  # Limit text length
            embedding = await self.embeddings.aembed_query(
                query_text
            )
            timestamp = datetime.utcnow()
            vector_id = f"req-{timestamp.timestamp()}"

            # Create vector metadata
            metadata = {
                "project_id": project_data.get("id"),
                "type": "requirement_analysis",
                "timestamp": (
                    timestamp.isoformat()
                ),
            }

            # Store in Pinecone
            vector = {
                "id": vector_id,
                "values": embedding,
                "metadata": metadata,
            }
            self.index.upsert(vectors=[vector])

            # Parse analysis if needed
            parsed = (
                json.loads(analysis)
                if isinstance(analysis, str)
                else analysis
            )

            # Return formatted response
            return {
                "status": "success",
                "analysis": parsed,
                "model_used": model,
            }

        except Exception as e:
            return {"status": "error", "error": str(e), "model_used": model}

    async def assess_project_risks(self, project_id: int) -> Dict[str, Any]:
        """Perform risk assessment and feasibility analysis.

        Args:
            project_id: ID of the project to assess.

        Returns:
            Dictionary containing risk assessment results and model info.
        """
        # Retrieve project context from vector store
        vector_size = 1536  # Size of embedding vector
        similar_projects = self.index.query(
            vector=[0] * vector_size,  # Would use actual project embedding
            top_k=5,
            include_metadata=True,
        )

        model, client = await self.select_model("requirement_analysis")

        prompt = (
            f"Based on the project context and similar projects, "
            f"perform a risk assessment and feasibility analysis.\n"
            f"Project ID: {project_id}\n"
            f"Similar Projects: {json.dumps(similar_projects)}\n\n"
            "Please provide:\n"
            "1. Technical risks and mitigation strategies\n"
            "2. Resource requirements and constraints\n"
            "3. Timeline feasibility\n"
            "4. Cost estimation\n"
            "5. Critical success factors"
        )

        try:
            if isinstance(client, openai.OpenAI):
                # Generate assessment using OpenAI
                completion = await client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=2000,
                )
                assessment = completion.choices[0].message.content
            elif isinstance(client, anthropic.Anthropic):
                # Generate assessment using Anthropic
                msg = await client.messages.create(
                    model=model,
                    max_tokens=2000,
                    messages=[{"role": "user", "content": prompt}],
                )
                assessment = msg.content[0].text

            # Parse assessment if needed
            assessment_data = (
                json.loads(assessment)
                if isinstance(assessment, str)
                else assessment
            )

            # Return formatted response
            return {
                "status": "success",
                "assessment": assessment_data,
                "model_used": model,
            }

        except Exception as e:
            return {"status": "error", "error": str(e), "model_used": model}
