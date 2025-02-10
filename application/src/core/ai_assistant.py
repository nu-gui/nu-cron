from typing import Dict, Any, List
import openai
import anthropic
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
import pinecone
import os
import json
from datetime import datetime

class AIAssistant:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.claude_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
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
        """
        Select the most appropriate AI model based on task type
        """
        model_mapping = {
            "requirement_analysis": ("gpt-4-turbo-preview", self.openai_client),
            "code_generation": ("gpt-4-turbo-preview", self.openai_client),
            "code_review": ("claude-3-opus", self.claude_client),
            "testing": ("mistral-7b", None),  # Placeholder for Mistral integration
        }
        return model_mapping.get(task_type, ("gpt-4-turbo-preview", self.openai_client))

    async def analyze_requirements(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze project requirements and generate structured documentation
        """
        model, client = await self.select_model("requirement_analysis")
        
        # Create prompt for requirement analysis
        prompt = f"""Analyze the following project requirements and generate structured documentation:
        Project Name: {project_data.get('name')}
        Description: {project_data.get('description')}
        Requirements: {json.dumps(project_data.get('requirements', []))}
        
        Please provide:
        1. Functional requirements breakdown
        2. Technical specifications
        3. Dependencies and constraints
        4. Risk assessment
        5. Implementation timeline
        """
        
        try:
            if isinstance(client, openai.OpenAI):
                response = await client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=2000
                )
                analysis = response.choices[0].message.content
            elif isinstance(client, anthropic.Anthropic):
                response = await client.messages.create(
                    model=model,
                    max_tokens=2000,
                    messages=[{"role": "user", "content": prompt}]
                )
                analysis = response.content[0].text
            
            # Store analysis in vector store
            embedding = await self.embeddings.aembed_query(analysis)
            self.index.upsert(
                vectors=[{
                    "id": f"req-{datetime.utcnow().timestamp()}",
                    "values": embedding,
                    "metadata": {
                        "project_id": project_data.get("id"),
                        "type": "requirement_analysis",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }]
            )
            
            return {
                "status": "success",
                "analysis": json.loads(analysis) if isinstance(analysis, str) else analysis,
                "model_used": model
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "model_used": model
            }

    async def assess_project_risks(self, project_id: int) -> Dict[str, Any]:
        """
        Perform risk assessment and feasibility analysis
        """
        # Retrieve project context from vector store
        similar_projects = self.index.query(
            vector=[0] * 1536,  # Placeholder vector, would use actual project embedding
            top_k=5,
            include_metadata=True
        )
        
        model, client = await self.select_model("requirement_analysis")
        
        prompt = f"""Based on the project context and similar projects, perform a risk assessment and feasibility analysis.
        Project ID: {project_id}
        Similar Projects: {json.dumps(similar_projects)}
        
        Please provide:
        1. Technical risks and mitigation strategies
        2. Resource requirements and constraints
        3. Timeline feasibility
        4. Cost estimation
        5. Critical success factors
        """
        
        try:
            if isinstance(client, openai.OpenAI):
                response = await client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=2000
                )
                assessment = response.choices[0].message.content
            elif isinstance(client, anthropic.Anthropic):
                response = await client.messages.create(
                    model=model,
                    max_tokens=2000,
                    messages=[{"role": "user", "content": prompt}]
                )
                assessment = response.content[0].text
            
            return {
                "status": "success",
                "assessment": json.loads(assessment) if isinstance(assessment, str) else assessment,
                "model_used": model
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "model_used": model
            }
