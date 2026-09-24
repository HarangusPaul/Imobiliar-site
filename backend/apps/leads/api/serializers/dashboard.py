"""Dashboard lead serializers."""

from __future__ import annotations

from rest_framework import serializers

from apps.leads.models import Lead, LeadNote, LeadStatus


class LeadNoteSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)
    author_name = serializers.CharField(source="author.get_full_name", read_only=True)

    class Meta:
        model = LeadNote
        fields = ["id", "body", "author_name", "is_system", "created_at"]
        read_only_fields = fields


class DashboardLeadListSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)
    subject_label = serializers.SerializerMethodField()
    assigned_to_name = serializers.CharField(source="assigned_to.get_full_name", read_only=True)

    class Meta:
        model = Lead
        fields = [
            "id",
            "kind",
            "status",
            "full_name",
            "phone_number",
            "email",
            "subject_label",
            "assigned_to_name",
            "created_at",
            "first_response_at",
        ]
        read_only_fields = fields

    def get_subject_label(self, lead: Lead) -> str | None:
        return str(lead.subject) if lead.subject is not None else None


class DashboardLeadDetailSerializer(DashboardLeadListSerializer):
    notes = LeadNoteSerializer(many=True, read_only=True)

    class Meta(DashboardLeadListSerializer.Meta):
        fields = DashboardLeadListSerializer.Meta.fields + [
            "message",
            "contact_preference",
            "preferred_time",
            "source_path",
            "request_id",
            "notes",
            "closed_at",
        ]
        read_only_fields = fields


class LeadStatusChangeSerializer(serializers.Serializer):
    target = serializers.ChoiceField(choices=LeadStatus.choices)
    note = serializers.CharField(max_length=2000, required=False, allow_blank=True, default="")


class LeadAssignmentSerializer(serializers.Serializer):
    assignee_id = serializers.UUIDField(allow_null=True)
    note = serializers.CharField(max_length=2000, required=False, allow_blank=True, default="")
